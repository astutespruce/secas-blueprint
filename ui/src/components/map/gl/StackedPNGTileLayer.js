import { TileLayer, _getURLFromTemplate } from '@deck.gl/geo-layers'
import { load } from '@loaders.gl/core'
import { Texture2D } from '@luma.gl/core'
import { ImageLoader } from '@loaders.gl/images'
import GL from '@luma.gl/constants'

import { sum } from 'util/data'

// have to use the raw loader to load shaders
/* eslint-disable-next-line */
import vertexShader from 'raw-loader!./vertex.vs'
/* eslint-disable-next-line */
import fragmentShader from 'raw-loader!./fragment.fs'

import StackedPNGLayer from './StackedPNGLayer'

/**
 * Fetch a tile image asynchronously and load into a GL texture
 * @param {Object} gl - WebGL context
 * @param {String} url - url of tile
 * @returns
 */
const fetchImage = async (gl, url) => {
  const data = await load(url, ImageLoader)

  if (!data) {
    return null
  }

  return new Texture2D(gl, {
    data,
    format: GL.RGBA,
    dataFormat: GL.RGBA,
    type: GL.UNSIGNED_BYTE,
    parameters: {
      [GL.TEXTURE_MIN_FILTER]: GL.NEAREST,
      [GL.TEXTURE_MAG_FILTER]: GL.NEAREST,
      [GL.TEXTURE_WRAP_S]: GL.CLAMP_TO_EDGE,
      [GL.TEXTURE_WRAP_T]: GL.CLAMP_TO_EDGE,
    },
    mipmaps: false,
  })
}

/**
 * Construct uniform of vec2 values of [minVal, maxVal] for each indicator.
 * maxVal is set to -1 to ignore this indicator when filtering.
 * @param {Array} encodingSchemes - array of encoding config
 * @param {Object} filterRanges - key:[minVal, maxVal] for filters
 */
const getFilterRanges = (encodingSchemes, filterRanges) => {
  const ranges = []

  encodingSchemes.forEach((layers) => {
    layers.forEach(({ id, valueShift }) => {
      let range = filterRanges[id]
      if (range) {
        if (range.length) {
          if (valueShift) {
            range = [range[0] + 1, range[1] + 1]
          }
        } else {
          // filter based on ABSENCE (nodata)
          range = [0, 0]
        }
      } else {
        range = [-1, -1]
      }
      ranges.push(...range)
    })
  })
  return ranges
}

/**
 * StackedPNGTileLayer provides a tile-loading interface that wraps
 * StackedPNGLayer instances (one per tile).
 */
export default class StackedPNGTileLayer extends TileLayer {
  initializeState() {
    super.initializeState()

    const { layers } = this.props

    const encodingSchemes = layers.map(({ encoding }) => encoding)

    this.setState({
      tileset: null,
      isLoaded: false,
      shaders: {
        vs: vertexShader,
        fs: fragmentShader.replace(
          '<NUM_INDICATORS>',
          sum(encodingSchemes.map((e) => e.length)).toString()
        ),
      },
    })
  }

  async getTileData(tile) {
    const { gl } = this.context

    // prevent fetching tiles if layer is not visible
    if (!this.props.visible) {
      return { images: null }
    }

    const imageRequests = this.props.layers.map(({ url }) =>
      fetchImage(gl, _getURLFromTemplate(url, tile))
    )

    const images = await Promise.all(imageRequests)
    return { images }
  }

  renderSubLayers(props) {
    const { shaders } = this.state
    const {
      tile: {
        bbox: { west, south, east, north },
      },
      layers,
      data: { images } = {},
      filters,
      renderTarget,
    } = props

    if (images === null) {
      return null
    }

    // TODO: figure out how to hoist this to state or memoize it:
    const filterRanges = getFilterRanges(
      layers.map(({ encoding }) => encoding),
      filters || {}
    )

    return new StackedPNGLayer(props, {
      shaders,
      bounds: [west, south, east, north],
      images,
      filterRanges,
      renderTarget,
    })
  }
}

StackedPNGTileLayer.layerName = 'StackedPNGTileLayer'
StackedPNGTileLayer.defaultProps = {
  ...TileLayer.defaultProps,
  filters: {},
  pickable: false,
}
