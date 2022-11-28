import { Texture2D } from '@luma.gl/core'
import GL from '@luma.gl/constants'

/**
 * Convert hex string to RGBA array
 * Only 6 character form is supported
 * @param {String} hex
 */
const hexToRGBA = (hex) => {
  if (hex === null) {
    return [0, 0, 0, 0]
  }

  if (hex.length === 9) {
    return [
      parseInt(`0x${hex[1]}${hex[2]}`, 16),
      parseInt(`0x${hex[3]}${hex[4]}`, 16),
      parseInt(`0x${hex[5]}${hex[6]}`, 16),
      parseInt(`0x${hex[7]}${hex[8]}`, 16),
    ]
  }
  return [
    parseInt(`0x${hex[1]}${hex[2]}`, 16),
    parseInt(`0x${hex[3]}${hex[4]}`, 16),
    parseInt(`0x${hex[5]}${hex[6]}`, 16),
    255,
  ]
}

/**
 * Create a flattened palette of RGBA values based on hex colors
 * @param {*} colors
 * @returns Uint8Array of RGBA data
 */
const makeRGBAPalette = (colors) => {
  const palette = []
  colors.forEach((c) => {
    palette.push(...hexToRGBA(c))
  })
  return new Uint8Array(palette)
}

/**
 * Create a WebGL texture from a palette of [R,G,B,A, ...]
 * values
 * @param {*} gl - WebGL context
 * @param {Uint8Array} palette - palette array of [R,G,B,A, ...] values
 * @returns WebGL texture
 */
const createTextureFromPalette = (gl, palette) =>
  new Texture2D(gl, {
    width: palette.length / 4,
    height: 1,
    data: palette,
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

export const createRenderTarget = (gl, pixelLayer, colors) => {
  // IMPORTANT: palette must always include as its first entry a color for nodata
  const palette = makeRGBAPalette([
    null, // nodata value
    ...colors,
  ])

  return {
    palette: createTextureFromPalette(gl, palette),
    ...pixelLayer,
  }
}
