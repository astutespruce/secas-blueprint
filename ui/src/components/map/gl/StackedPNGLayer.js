import { project32 } from '@deck.gl/core'
import { BitmapLayer } from '@deck.gl/layers'

class StackedPNGLayer extends BitmapLayer {
  draw({ uniforms }) {
    const { model } = this.state
    const { bounds, images, opacity, filterValues, renderTarget } = this.props

    if (
      !model ||
      !images ||
      images.length === 0 ||
      !images.every((item) => item)
    ) {
      return
    }

    const layerImages = images.reduce((prev, cur, i) => {
      Object.assign(prev, { [`layer${i}`]: cur })
      return prev
    }, {})

    model
      .setUniforms(uniforms)
      .setUniforms({
        ...layerImages,
        bounds,
        filterValues,
        renderLayerPalette: renderTarget.palette,
        renderLayerPaletteSize: renderTarget.palette.width,
        renderLayerTextureIndex: renderTarget.textureIndex,
        renderLayerOffset: renderTarget.offset,
        renderLayerBits: renderTarget.bits,
        opacity,
      })
      .draw()
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
