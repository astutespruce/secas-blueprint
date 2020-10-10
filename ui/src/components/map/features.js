import {
  applyFactor,
  parsePipeEncodedValues,
  parseDeltaEncodedValues,
  parseDictEncodedValues,
} from 'util/data'

const isEmpty = (text) => {
  if (!text) {
    return true
  }
  if (text === '"') {
    return true
  }

  return false
}

/**
 * Unpack encoded attributes in feature data.
 * NOTE: indicators are returned by their index, not id.
 * @param {Object} properties
 */
export const unpackFeatureData = (properties) => {
  const values = Object.entries(properties)
    .map(([key, value]) => {
      if (!value || typeof value !== 'string') {
        return [key, value]
      }

      if (isEmpty(value)) {
        return [key, null]
      }

      if (key === 'name') {
        return [key, value]
      }

      if (value.indexOf('^') !== -1) {
        return [key, parseDeltaEncodedValues(value)]
      }
      if (value.indexOf(':') !== -1) {
        return [key, parseDictEncodedValues(value)]
      }
      if (value.indexOf('|') !== -1) {
        return [key, parsePipeEncodedValues(value)]
      }
      return [key, value]
    })
    .reduce((prev, [key, value]) => {
      // eslint-disable-next-line no-param-reassign
      prev[key] = value
      return prev
    }, {})

  // rescale specific things from percent * 10 back to percent

  values.blueprint = values.blueprint ? applyFactor(values.blueprint, 0.1) : []
  values.inputs = values.inputs ? applyFactor(values.inputs, 0.1) : []

  values.okchatrank = values.okchatrank
    ? applyFactor(values.okchatrank, 0.1)
    : []
  values.txchatrank = values.txchatrank
    ? applyFactor(values.txchatrank, 0.1)
    : []

  // merge avg and percents together
  if (values.indicators) {
    Object.keys(values.indicators).forEach((k) => {
      const percent = applyFactor(values.indicators[k], 0.1)

      values.indicators[k] = {
        percent,
        // calculate avg bin from percents if not a continuous indicator
        avg: values.indicator_avg ? values.indicator_avg[k] || null : null,
      }
    })
  } else {
    values.indicators = []
  }

  if (values.slr) {
    values.slr = applyFactor(values.slr, 0.1)
  }

  if (values.urban) {
    values.urban = applyFactor(values.urban, 0.1)
  }

  if (values.ownership) {
    Object.keys(values.ownership).forEach((k) => {
      values.ownership[k] *= 0.1
    })
  }

  if (values.protection) {
    Object.keys(values.protection).forEach((k) => {
      values.protection[k] *= 0.1
    })
  }

  // rename specific fields for easier use later
  values.blueprintAcres = values.blueprint_total
  values.analysisAcres = values.shape_mask
  values.unitType = values.type
  values.unitAcres = values.acres

  console.log('transformed feature data', values)

  return values
}
