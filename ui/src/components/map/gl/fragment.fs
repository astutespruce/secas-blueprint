#define SHADER_NAME stackedpng_fragment_shader

#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif

varying vec2 vTexCoord;

// uniforms for rendering the output after filtering
uniform float opacity;
uniform int renderLayerTextureIndex;
uniform float renderLayerOffset;
uniform float renderLayerBits;
uniform sampler2D renderLayerPalette;
uniform float renderLayerPaletteSize;

// uniforms for textures of indicator tiles
uniform sampler2D indicator0;
uniform sampler2D indicator1;
uniform sampler2D indicator2;
uniform sampler2D indicator3;
uniform sampler2D indicator4;
uniform sampler2D indicator5;

// pairs of [minVal, maxVal] for each indicator; [-1, -1] indicates no filtering
// for that indicator
// count is filled from JS since this can't be dynamic in the shader
uniform vec2 ranges[<NUM_INDICATORS>];

// return 32-bit integer(ish)
float rgbToInt32(vec3 v) {
  // equivalent of (r << 16) + (g << 8) + b
  return (v.r * 65536.) + (v.g * 256.) + v.b;
}

bool isOdd(float v) { return (v - (floor(v * 0.5) * 2.0)) > 0.5; }

// bitwise and (32 bit) adapted from:
// https://gist.github.com/EliCDavis/f35a9e4afb8e1c9ae94cce8f3c2c9b9a
float bitwise_and(float v1, float v2) {
  float byte_val = 1.0;
  float result = 0.0;

  // iterate over each bit, stop when either bit is 0
  for (int i = 0; i < 32; i++) {
    if (v1 == 0.0 || v2 == 0.0) {
      return result;
    }

    float both_bytes_1 = isOdd(v1) && isOdd(v2) ? 1.0 : 0.0;

    result += both_bytes_1 * byte_val;
    v1 = floor(v1 / 2.0);
    v2 = floor(v2 / 2.0);
    byte_val *= 2.0;
  }
  return result;
}

float rshift(float v, float num) {
  return (num == 0.0) ? v : floor(v / pow(2.0, num));
}

// calculate bitmask for extracting number of bits from an integer (using
// floating point math)
float bitmask(float bits) { return pow(2.0, bits) - 1.0; }

bool withinRange(float valueRGB, float offset, float numBits, vec2 range) {
  float value = bitwise_and(rshift(valueRGB, offset), bitmask(numBits));
  return (value >= range[0] && value <= range[1]);
}

void main(void) {
  // canRender is True where all filters are either not set or values are
  // within range

  // <FILTER_EXPR>
  // FIXME: this will instead come from filter expr
  bool canRender = true;

  float valueRGB;
  if (renderLayerTextureIndex == 0) {
    valueRGB = rgbToInt32(texture2D(indicator0, vTexCoord).rgb * 255.0);
  } else if (renderLayerTextureIndex == 1) {
    valueRGB = rgbToInt32(texture2D(indicator1, vTexCoord).rgb * 255.0);
  } else if (renderLayerTextureIndex == 2) {
    valueRGB = rgbToInt32(texture2D(indicator2, vTexCoord).rgb * 255.0);
  } else if (renderLayerTextureIndex == 3) {
    valueRGB = rgbToInt32(texture2D(indicator3, vTexCoord).rgb * 255.0);
  } else if (renderLayerTextureIndex == 4) {
    valueRGB = rgbToInt32(texture2D(indicator4, vTexCoord).rgb * 255.0);
  } else if (renderLayerTextureIndex == 5) {
    valueRGB = rgbToInt32(texture2D(indicator5, vTexCoord).rgb * 255.0);
  }
  float renderValue = bitwise_and(rshift(valueRGB, renderLayerOffset),
                                  bitmask(renderLayerBits));

  vec4 color = vec4(renderValue / 255.0, 0., 0., 1.);

  // FIXME: re-enable
  // vec4 color = texture2D(renderLayerPalette,
  //                        vec2(renderValue / renderLayerPaletteSize, 0.5));

  // color.a = color.a * opacity;

  // if (!canRender) {
  //   color.a = 0.0;
  // }

  gl_FragColor = color;
}