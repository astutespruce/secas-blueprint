/**
 * Construct WebGL filter expressions to inject into fragment shader
 * because we can't do this in a loop in the shader.
 * The ranges are defined in getFilterRanges below.
 * @param {Array} encodingSchemes - array of encoding config
 * @returns GLSL code to inject into the fragment shader
 */
export const getFilterExpr = (encodingSchemes) => {
  let code = ''
  const conditions = []
  let i = 0
  encodingSchemes.forEach((layers, textureIndex) => {
    const expressions = []
    layers.forEach(({ offset, bits }) => {
      expressions.push(
        `\n((ranges[${i}][1] < 0.0) || withinRange(valueRGB${textureIndex}, ${offset}.0, ${bits}.0, ranges[${i}]))`
      )
      i += 1
    })

    const condition = `canRender${textureIndex}`
    conditions.push(condition)

    code += `\nbool ${condition} = (${expressions.join(' &&')});\n`
  })

  return `\n${code}\n\nbool canRender = (${conditions.join(' && ')});\n`
}

/**
 * Construct uniform of vec2 values of [minVal, maxVal] for each indicator.
 * maxVal is set to -1 to ignore this indicator when filtering.
 * @param {Array} encodingSchemes - array of encoding config
 * @param {Object} filterRanges - key:[minVal, maxVal] for filters
 */
export const getFilterRanges = (encodingSchemes, filterRanges) => {
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
