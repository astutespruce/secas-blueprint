/* eslint-disable no-bitwise */

import { readPixelsToArray } from '@luma.gl/core'
import GL from '@luma.gl/constants'

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

export const extractPixelData = (map, point, layer) => {
  const screenPoint = map.project(point)

  // FIXME: this is no longer resolving a tile correctly
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
  layers.forEach(({ encoding }, i) => {
    const pixelValue = pixelValues[i]
    if (pixelValue === 0) {
      // console.debug('pixel value is 0')
      // if entire pixel is 0 (NODATA), it can be ignored
      return
    }

    encoding.forEach(({ id, offset, bits, valueShift = 0 }) => {
      let value = (pixelValue >> offset) & (2 ** bits - 1)
      if (value && valueShift) {
        value -= valueShift
      }
      data[id] = value
    })
  })

  // if data.blueprint === 0, then pixel is is outside base blueprint area

  return data
}
