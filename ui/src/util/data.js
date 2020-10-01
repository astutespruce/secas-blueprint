/**
 * Flatten an array of arrays (2D) to an array (1D)
 * @param {Array} records
 */
export const flatten = (records) =>
  records.reduce((prev, record) => {
    prev.push(...record)
    return prev
  }, [])

/**
 * Convert an array to an object, indexing on values of field
 * @param {Array} records
 * @param {String} field
 */
export const indexBy = (records, field) =>
  records.reduce(
    (prev, record) => Object.assign(prev, { [record[field]]: record }),
    {}
  )

/**
 * Calculate the sum of an array of numbers
 * @param {Array} values - array of numbers
 */
export const sum = (values) => values.reduce((prev, value) => prev + value, 0)

/**
 * Calculate the min and max values for an array of numbers
 * @param {Array} values
 */
export const extent = (values) => {
  return [Math.min(...values), Math.max(...values)]
}

export const sortByFunc = (field, ascending = true) => (a, b) => {
  if (a[field] < b[field]) {
    return ascending ? -1 : 1
  }
  if (a[field] > b[field]) {
    return ascending ? 1 : -1
  }
  return 0
}

export const applyFactor = (values, factor) => {
  if (!values) return values

  return values.map((v) => v * factor)
}

/**
 * Calculate the average bin based on using percents vs total percent as weights
 * and bin index as value.
 * @param {*} percents
 */
export const percentsToAvg = (percents) => {
  const total = sum(percents)
  return sum(percents.map((p, i) => i * (p / total)))
}

const numericRegex = /\d+/
const nonNumericRegex = /[^0-9|]/

/**
 * Parse a pipe-delimited string of integers,strings, or blanks into an array of values.
 * Blanks are assumed to be 0.
 * "498||405|90|7" => [498, 0, 405, 90, 7]
 * "foo|bar" => ["foo", "bar"]
 * @param {String} text
 */
export const parsePipeEncodedValues = (text) => {
  if (!text) return null

  const parts = text.split('|')

  if (nonNumericRegex.test(text)) {
    return parts
  }

  return parts.map((d) => parseInt(d, 10) || 0)
}

/**
 * Parse delta-encoded string of integers or blanks into an array of values.
 * First value is always the baseline.  If delta values are absent, this assumes
 * there is no change.
 * "66^23^13^7^15^10^9" => [66, 89, 102, 109, 124, 134, 143]
 *
 * @param {String} text
 */
export const parseDeltaEncodedValues = (text) => {
  if (!text) return null

  const [baseline, ...deltas] = text.split('^').map((d) => parseInt(d, 10) || 0)

  const values = [baseline, ...Array(deltas.length)]
  for (let i = 1; i < values.length; i += 1) {
    values[i] = values[i - 1] + deltas[i - 1]
  }

  return values
}

/**
 * Parse dictionary encoded values to object.  Values may be pipe encoded.
 * Numeric values are parsed to floats.
 * "0:|437|||,1:|438|||" => {0: [0, 437, 0, 0, 0], 1: [0, 438, 0, 0, 0]}
 * @param {String} text
 */
export const parseDictEncodedValues = (text) => {
  if (!text) return null

  return text
    .split(',')
    .map((d) => d.split(':'))
    .map(([k, v]) => {
      if (v !== null && v !== undefined && v.indexOf('|') !== -1) {
        return [k, parsePipeEncodedValues(v)]
      }

      if (numericRegex.test(v)) {
        return [k, parseFloat(v)]
      }

      return [k, v]
    })
    .reduce((prev, [k, v]) => {
      // eslint-disable-next-line no-param-reassign
      prev[k] = v
      return prev
    }, {})
}
