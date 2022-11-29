/* eslint-disable no-bitwise */

import { readPixelsToArray } from '@luma.gl/core'
import GL from '@luma.gl/constants'

import { indexBy } from 'util/data'

const TILE_SIZE = 512

/**
 * Read a single pixel from a texture created from a PNG tile image into a
 * single uint32 value (RGB value only, alpha is ignored).
 * @param {*} texture - WebGL texture
 * @param {*} offsetX - offset x value into image
 * @param {*} offsetY - offset y value into image
 * @returns uint32 value
 */
export const readPixelToUint32 = (texture, offsetX, offsetY) => {
  const pixel = readPixelsToArray(texture, {
    sourceX: offsetX,
    sourceY: offsetY,
    sourceFormat: GL.RGBA,
    sourceWidth: 1,
    sourceHeight: 1,
    sourceType: GL.UNSIGNED_BYTE,
  })

  // decode to uint32, ignoring alpha value, which will be 0 for NODATA / empty tiles or 255
  const [r, g, b] = pixel

  const value = (r << 16) | (g << 8) | b

  // console.debug('read pixel', [...pixel], '=>', value)

  return value
}

const getTileID = (
  zoom,
  mercX,
  mercY,
  minZoom,
  maxZoom,
  tileSize = TILE_SIZE
) => {
  // zoom adapted from: https://github.com/visgl/deck.gl/blob/8.7-release/modules/geo-layers/src/tile-layer/utils.js::getTileIndices
  let z = Math.round(zoom + Math.log2(TILE_SIZE / tileSize))
  // clip to [minZoom, maxZoom]
  if (Number.isFinite(minZoom) && z < minZoom) {
    z = minZoom
  } else if (Number.isFinite(maxZoom) && z > maxZoom) {
    z = maxZoom
  }

  const numTilesAtZoom = 1 << z
  return {
    z,
    x: Math.floor(mercX * numTilesAtZoom),
    y: Math.floor(mercY * numTilesAtZoom),
  }
}

export const getTile = (map, screenPoint, layer) => {
  // resolve the StackedPNGTileLayer; layers[1:n] are StackedPNGLayers
  const tileLayer = layer.implementation.deck.layerManager.layers[0]
  const {
    props: { minZoom, maxZoom, tileSize },
    state: { tileset },
  } = tileLayer

  // calculate tile containing point
  const { x: mercX, y: mercY } = map.transform.pointCoordinate(screenPoint)
  const tileID = getTileID(
    map.getZoom(),
    mercX,
    mercY,
    minZoom,
    maxZoom,
    tileSize
  )

  // rescale Mercator coordinates to tile coords
  const scale = (2 ** tileID.z * TILE_SIZE) / tileSize
  const offsetX = Math.floor((mercX * scale - tileID.x) * tileSize)
  const offsetY = Math.floor((mercY * scale - tileID.y) * tileSize)

  // const searchID = `${tileID.x}-${tileID.y}-${tileID.z}`
  const { z: searchZ, x: searchX, y: searchY } = tileID

  // tileset.selectedTiles  contain all tiles at current zoom level
  const [tile] = tileset.selectedTiles.filter(
    ({ z, x, y }) => z === searchZ && x === searchX && y === searchY
  )
  return {
    tile: tile || null,
    offsetX,
    offsetY,
  }
}

const extractIndicators = (data, ecosystemInfo, indicatorInfo) => {
  const ecosystemIndex = indexBy(ecosystemInfo, 'id')

  let hasInland = false
  let hasMarine = false

  let indicators = indicatorInfo.map(
    ({ id, values: valuesInfo, ...indicator }) => {
      const present = data[id] !== undefined && data[id] !== null

      if (present) {
        if (id.startsWith('base:land_') || id.startsWith('base:freshwater_')) {
          hasInland = true
        } else {
          hasMarine = true
        }
      }

      const values = valuesInfo.map(({ value, ...rest }) => ({
        ...rest,
        value,
        percent: data[id] === value ? 100 : 0,
      }))

      return {
        ...indicator,
        id,
        values,
        total: present ? 100 : 0,
        ecosystem: ecosystemIndex[id.split(':')[1].split('_')[0]],
      }
    }
  )

  if (!hasInland) {
    indicators = indicators.filter(({ id }) => id.search('marine_') !== -1)
  } else if (!hasMarine) {
    // has no marine, likely inland, don't show any marine indicators
    indicators = indicators.filter(({ id }) => id.search('marine_') === -1)
  }

  indicators = indexBy(indicators, 'id')

  // aggregate these up by ecosystems for ecosystems that are present
  const ecosystemsPresent = new Set(
    Object.keys(indicators).map((id) => id.split(':')[1].split('_')[0])
  )

  const ecosystems = ecosystemInfo
    .filter(({ id }) => ecosystemsPresent.has(id))
    .map(
      ({
        id: ecosystemId,
        label,
        color,
        borderColor,
        indicators: ecosystemIndicators,
        ...rest
      }) => {
        const indicatorsPresent = ecosystemIndicators.filter(
          (indicatorId) => indicators[indicatorId]
        )

        return {
          ...rest,
          id: ecosystemId,
          label,
          color,
          borderColor,
          indicators: indicatorsPresent.map((indicatorId) => ({
            ...indicators[indicatorId],
          })),
        }
      }
    )

  return { ecosystems, indicators }
}

export const extractPixelData = (
  map,
  point,
  layer,
  ecosystemInfo,
  indicatorInfo
) => {
  const screenPoint = map.project(point)

  const { tile, offsetX, offsetY } = getTile(map, screenPoint, layer)

  if (!(tile && tile.data && tile.data.images)) {
    console.debug('no tile available')
    // Note: this is a special case because it happens while map is still loading
    // and tileset claims it is loaded, but for the wrong zoom levels
    return null
  }

  // console.debug('tile', tile)

  // images are at tile.data.images
  const {
    data: { images },
  } = tile

  const pixelValues = images.map((image) =>
    readPixelToUint32(image, offsetX, offsetY)
  )

  // decode pixel values
  const {
    implementation: {
      props: { layers },
    },
  } = layer

  const data = {}

  // layers will be empty array if there are no tiles for any of the pixel layers
  layers.forEach(({ encoding }, i) => {
    const pixelValue = pixelValues[i]
    if (pixelValue === 0) {
      // console.debug('pixel value is 0')
      // if entire pixel is 0 (NODATA), it can be ignored
      return
    }

    encoding.forEach(({ id, offset, bits, valueShift = 0 }) => {
      let value = (pixelValue >> offset) & (2 ** bits - 1)
      // if value is 0, it is NODATA
      if (value > 0) {
        value -= valueShift
        data[id] = value
      }
    })
  })

  // if data is empty, then pixel is is outside base blueprint area
  if (Object.keys(data).length === 0) {
    return {
      inputId: null,
    }
  }

  // unpack indicators and ecosystems
  data.indicators = {
    base: extractIndicators(data, ecosystemInfo, indicatorInfo.base.indicators),
  }

  // extract ownership info
  const ownership = {}
  const protection = {}
  const protectedAreas = []
  const ownershipFeatures = map.queryRenderedFeatures(screenPoint, {
    layers: ['ownership'],
  })

  if (ownershipFeatures.length > 0) {
    ownershipFeatures.forEach(
      ({
        properties: {
          Loc_Own: owner,
          GAP_Sts: gapStatus,
          Loc_Nm: areaName,
          Own_Type: orgType,
        },
      }) => {
        // hardcode in percent
        ownership[orgType] = 100
        protection[gapStatus] = 100
        protectedAreas.push({ name: areaName, owner })
      }
    )
  }

  return {
    inputId: 'base', // pixel data only available for SE Base Blueprint area
    outsideSEPercent: 0,
    ...data,
    ownership,
    protection,
    protectedAreas,
  }
}
