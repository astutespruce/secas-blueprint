import { project32 } from '@deck.gl/core'
import { BitmapLayer } from '@deck.gl/layers'
import GL from '@luma.gl/constants'
import { Framebuffer, Texture2D, readPixelsToArray } from '@luma.gl/core'

import { histogram } from 'util/data'
// import { readTexturePixels } from './framebuffer'

const rgbaToHex = (arr) => {
  let r
  let g
  let b
  let a
  const out = []
  for (let i = 0; i < arr.length; i += 4) {
    r = arr[i]
    g = arr[i + 1]
    b = arr[i + 2]
    a = arr[i + 3]
    out.push(
      `#${r ? r.toString(16) : '00'}${g ? g.toString(16) : '00'}${
        b ? b.toString(16) : '00'
      }${a ? a.toString(16) : '00'}`
    )
  }
  return out
}

// window.rgbaToHex = rgbaToHex
// window.histogram = histogram

class StackedPNGLayer extends BitmapLayer {
  draw({ uniforms }) {
    const { model } = this.state
    const { bounds, images, opacity, filterRanges, renderTarget } = this.props

    // console.log('draw', this, images)
    // if (this.id === 'pixelLayers-1-3-3') {
    //   console.log('read pixels from', images[0])
    //   const [{ width, height, _handle: texture }] = images
    //   const pixels = readTexturePixels(this.context.gl, texture, width, height)
    //   console.log('read raw pixels from image', histogram(pixels))
    // }

    if (
      !model ||
      !images ||
      images.length === 0 ||
      !images.every((item) => item)
    ) {
      return
    }

    const indicatorImages = images.reduce((prev, cur, i) => {
      Object.assign(prev, { [`indicator${i}`]: cur })
      return prev
    }, {})

    model
      .setUniforms(uniforms)
      .setUniforms({
        ...indicatorImages,
        bounds,
        ranges: filterRanges,
        renderLayerPalette: renderTarget.palette,
        renderLayerPaletteSize: renderTarget.palette.width,
        renderLayerTextureIndex: renderTarget.textureIndex,
        renderLayerOffset: renderTarget.offset,
        renderLayerBits: renderTarget.bits,
        opacity,
      })
      .draw()

    if (this.id === 'pixelLayers-142-201-9') {
      // console.log('try to render to framebuffer', this.context.gl)
      const framebuffer = new Framebuffer(this.context.gl, {
        // width: 512,
        // height: 512,
        width: window.innerWidth,
        height: window.innerHeight,
      })

      const texture = new Texture2D(this.context.gl, {
        mipmaps: false,
        parameters: {
          [GL.TEXTURE_MIN_FILTER]: GL.NEAREST,
          [GL.TEXTURE_MAG_FILTER]: GL.NEAREST,
          [GL.TEXTURE_WRAP_S]: GL.CLAMP_TO_EDGE,
          [GL.TEXTURE_WRAP_T]: GL.CLAMP_TO_EDGE,
        },
      })

      framebuffer.attach({
        [GL.COLOR_ATTACHMENT0]: texture,
      })
      framebuffer.checkStatus()
      model.draw({ framebuffer })
      const pixels = readPixelsToArray(framebuffer, {
        sourceX: 0,
        sourceY: 0,
        sourceFormat: GL.RGBA,
        sourceWidth: 512,
        sourceHeight: 512,
        sourceType: GL.UNSIGNED_BYTE,
      })
      // TODO: transform to hex colors, can ignore alpha
      console.log(this)
      // console.log('read pixels', pixels)
      // window.pixels = pixels
      console.log('pixels', histogram(pixels))
      // console.log('rendered colors: ', histogram(rgbaToHex(pixels)))
    }
  }

  getShaders() {
    const {
      shaders: { vs, fs },
    } = this.props

    const parentShaders = super.getShaders()
    return {
      ...parentShaders,
      vs,
      fs,
      modules: [project32],
    }
  }

  finalizeState() {
    super.finalizeState()

    if (this.state.images) {
      Object.values(this.state.images).forEach((image) => {
        if (image) {
          image.delete()
        }
      })
    }
  }
}

StackedPNGLayer.defaultProps = {
  ...BitmapLayer.defaultProps,
  pickable: false,
  images: { type: 'object', value: {}, compare: true },
  opacity: 1,
}
StackedPNGLayer.layerName = 'StackedPNGLayer'

export default StackedPNGLayer
