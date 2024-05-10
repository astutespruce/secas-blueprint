/* eslint-disable no-bitwise */

import { indexBy, setIntersection, sum } from 'util/data'

const TILE_SIZE = 512

/**
 * Read a single pixel from a texture created from a PNG tile image into a
 * single uint32 value (RGB value only, alpha is ignored).
 * @param {*} texture - WebGL texture
 * @param {*} offsetX - offset x value into image
 * @param {*} offsetY - offset y value into image
 * @returns uint32 value
 */
const readPixelToUint32 = (texture, offsetX, offsetY) => {
  // console.log('readPixelToUint32', texture, offsetX, offsetY)

  // read R,G,B, ignoring alpha
  let pixel = null
  const buffer = texture.device.createBuffer({ byteLength: 4 })
  try {
    const cmd = texture.device.createCommandEncoder()
    cmd.copyTextureToBuffer({
      source: texture,
      width: 1,
      height: 1,
      origin: [offsetX, offsetY],
      destination: buffer,
    })
    cmd.finish()
    pixel = buffer.readSyncWebGL()
  } finally {
    buffer.destroy()
  }

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

const getTile = (map, screenPoint, layer) => {
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
    ({ index: { z, x, y } }) => z === searchZ && x === searchX && y === searchY
  )
  return {
    tile: tile || null,
    offsetX,
    offsetY,
  }
}

const extractIndicators = (data, ecosystemInfo, indicatorInfo, subregions) => {
  const ecosystemIndex = indexBy(ecosystemInfo, 'id')

  // only show indicators that are either present or likely present based on
  // subregion
  let indicators = indicatorInfo
    .filter(({ id, subregions: indicatorSubregions }) => {
      const present = data[id] !== undefined && data[id] !== null
      return (
        present || setIntersection(indicatorSubregions, subregions).size > 0
      )
    })
    .map(({ id, values: valuesInfo, ...indicator }) => {
      const present = data[id] !== undefined && data[id] !== null

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
        ecosystem: ecosystemIndex[id.split('_')[0]],
      }
    })

  // aggregate these up by ecosystems for ecosystems that are present
  const ecosystemsPresent = new Set(
    indicators
      .filter(({ values }) => sum(values.map(({ percent }) => percent)) > 0)
      .map(({ ecosystem: { id } }) => id)
  )

  indicators = indexBy(indicators, 'id')

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
    // console.debug('no tile available')
    // Note: this is a special case because it happens while map is still loading
    // and tileset claims it is loaded, but for the wrong zoom levels
    return null
  }

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

  // if data is empty, then pixel is is outside blueprint area
  if (Object.keys(data).length === 0) {
    return {}
  }

  // extract info from feature data
  const features = map.queryRenderedFeatures(screenPoint, {
    layers: ['ownership', 'subregions'],
  })

  const [{ properties: { subregion } } = { properties: {} }] = features.filter(
    ({ layer: { id } }) => id === 'subregions'
  )

  const subregions = new Set([subregion])

  // unpack indicators and ecosystems
  data.indicators = extractIndicators(
    data,
    ecosystemInfo,
    indicatorInfo,
    subregions
  )

  // extract SLR
  if (data.slr !== undefined && data.slr !== null) {
    if (data.slr <= 10) {
      data.slr = {
        depth: data.slr,
        nodata: null,
      }
    } else {
      data.slr = {
        depth: null,
        nodata: data.slr - 11,
      }
    }
  } else {
    data.slr = {
      depth: null,
      nodata: null,
    }
  }

  // extract ownership info
  const ownership = {}
  const protection = {}
  const protectedAreas = []
  const ownershipFeatures = features.filter(
    ({ layer: { id } }) => id === 'ownership'
  )
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
    subregions,
    outsideSEPercent: 0,
    ...data,
    ownership,
    protection,
    protectedAreas,
  }
}
