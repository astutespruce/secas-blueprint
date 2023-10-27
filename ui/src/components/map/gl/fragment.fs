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

// uniforms for textures for each layer
uniform sampler2D layer0;
uniform sampler2D layer1;
uniform sampler2D layer2;
uniform sampler2D layer3;
uniform sampler2D layer4;
uniform sampler2D layer5;
uniform sampler2D layer6;
uniform sampler2D layer7;
uniform sampler2D layer8;

// encoded filters, with a bit set to 1 for each value that is present in the
// set of activated filters.  -1 indicates no filtering for that layer.
// NOTE: array size is filled from JS since this can't be dynamic in the shader
uniform float filterValues[<NUM_LAYERS>];

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

// shift v num bits right
float rshift(float v, float num) {
  return (num == 0.0) ? v : floor(v / pow(2.0, num));
}

// shift v num bits left
float lshift(float v, float num) {
  return (num == 0.0) ? v : v * pow(2.0, num);
}

// calculate bitmask for extracting number of bits from an integer (using
// floating point math)
float bitmask(float bits) { return pow(2.0, bits) - 1.0; }

bool matchValue(float valueRGB, float offset, float numBits,
                float filterValue) {
  float value = bitwise_and(rshift(valueRGB, offset), bitmask(numBits));

  // use left shift to set the bit in the value position to 1
  // then use bitwise AND to verify that value is also turned on in active
  // filters. If the value is 0, then value is not present in active filters.
  return bitwise_and(filterValue, lshift(1.0, value)) > 0.0;
}

void main(void) {
  float valueRGB0 = rgbToInt32(texture2D(layer0, vTexCoord).rgb * 255.0);
  float valueRGB1 = rgbToInt32(texture2D(layer1, vTexCoord).rgb * 255.0);
  float valueRGB2 = rgbToInt32(texture2D(layer2, vTexCoord).rgb * 255.0);
  float valueRGB3 = rgbToInt32(texture2D(layer3, vTexCoord).rgb * 255.0);
  float valueRGB4 = rgbToInt32(texture2D(layer4, vTexCoord).rgb * 255.0);
  float valueRGB5 = rgbToInt32(texture2D(layer5, vTexCoord).rgb * 255.0);
  float valueRGB6 = rgbToInt32(texture2D(layer6, vTexCoord).rgb * 255.0);
  float valueRGB7 = rgbToInt32(texture2D(layer7, vTexCoord).rgb * 255.0);
  float valueRGB8 = rgbToInt32(texture2D(layer8, vTexCoord).rgb * 255.0);

  // canRender is True where all filters are either not set or value is one
  // of active filter values

  // replaced dynamically from JS; sets canRender
  // <FILTER_EXPR>

  // bool canRender = true;

  float valueRGB;
  if (renderLayerTextureIndex == 0) {
    valueRGB = valueRGB0;
  }
  else if (renderLayerTextureIndex == 1) {
    valueRGB = valueRGB1;
  } else if (renderLayerTextureIndex == 2) {
    valueRGB = valueRGB2;
  } else if (renderLayerTextureIndex == 3) {
    valueRGB = valueRGB3;
  } else if (renderLayerTextureIndex == 4) {
    valueRGB = valueRGB4;
  } else if (renderLayerTextureIndex == 5) {
    valueRGB = valueRGB5;
  } else if (renderLayerTextureIndex == 6) {
    valueRGB = valueRGB6;
  } else if (renderLayerTextureIndex == 7) {
    valueRGB = valueRGB7;
  } else if (renderLayerTextureIndex == 8) {
    valueRGB = valueRGB8;
  }

  float renderValue = bitwise_and(rshift(valueRGB, renderLayerOffset),
                                  bitmask(renderLayerBits));

  // subtracting 0.1 from layer palette size is required to get this to work
  // properly on multiple graphics cards
  vec4 color =
      texture2D(renderLayerPalette,
                vec2(renderValue / (renderLayerPaletteSize - 0.1), 0.5));

  color.a = color.a * opacity;
  if (!canRender) {
    color.a = 0.0;
  }

  gl_FragColor = color;
}