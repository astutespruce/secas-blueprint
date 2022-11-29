import camelCase from 'camelcase'

import {
  applyFactor,
  parsePipeEncodedValues,
  parseDeltaEncodedValues,
  parseDictEncodedValues,
  indexBy,
  sum,
} from 'util/data'

/**
 * Return true if text is null or an empty string or single quote.
 * @param {String} text
 */
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
 * Extract dictionary-encoded counts and means
 * @param {Object} packedPercents
 * @param {Object} ecosystemInfo - array of ecosystem info
 * @param {Object} indicatorInfo - lookup of indicator info by index
 */
const extractIndicators = (
  packedPercents,
  ecosystemInfo,
  indicatorInfo,
  type
) => {
  const ecosystemIndex = indexBy(ecosystemInfo, 'id')

  // merge incoming packed percents with indicator info
  let indicators = indicatorInfo.map(
    ({ values: valuesInfo, ...indicator }, i) => {
      const present = !!packedPercents[i]

      const percents = present ? applyFactor(packedPercents[i], 0.1) : []

      // merge percent into values
      const values = valuesInfo.map((value, j) => ({
        ...value,
        percent: present ? percents[j] : 0,
      }))

      return {
        percent: percents,
        ...indicator,
        values,
        total: Math.min(sum(percents), 100),
        ecosystem: ecosystemIndex[indicator.id.split(':')[1].split('_')[0]],
      }
    }
  )

  // includes indicators that may be present in coastal areas
  const hasMarine =
    indicators.filter(
      ({ id, total }) => id.search('marine_') !== -1 && total > 0
    ).length > 0

  if (!hasMarine) {
    // has no marine, likely inland, don't show any marine indicators
    indicators = indicators.filter(({ id }) => id.search('marine_') === -1)
  } else if (type === 'marine lease block') {
    // has no inland
    indicators = indicators.filter(({ id }) => id.search('marine_') !== -1)
  }

  indicators = indexBy(indicators, 'id')

  // aggregate these up by ecosystems for ecosystems that are present
  const ecosystemsPresent = new Set(
    Object.keys(indicators).map((id) => id.split(':')[1].split('_')[0])
  )

  const ecosystems = ecosystemInfo
    .filter(({ id }) => ecosystemsPresent.has(id))
    .map(
      ({
        id: ecosystemId,
        label,
        color,
        borderColor,
        indicators: ecosystemIndicators,
        ...rest
      }) => {
        const indicatorsPresent = ecosystemIndicators.filter(
          (indicatorId) => indicators[indicatorId]
        )

        return {
          ...rest,
          id: ecosystemId,
          label,
          color,
          borderColor,
          indicators: indicatorsPresent.map((indicatorId) => ({
            ...indicators[indicatorId],
          })),
        }
      }
    )

  return { ecosystems, indicators }
}

/**
 * Unpack encoded attributes in feature data.
 * NOTE: indicators are returned by their index within their input (e.g., southatlantic), not id.
 * @param {Object} properties
 * @param {Object} inputs - lookup of input area info by input area id
 * @param {Object} ecosystemInfo - array of ecosystem info
 * @param {Object} indicatorValues - mapping of index in input to indicator object
 */
export const unpackFeatureData = (properties, ecosystemInfo, indicatorInfo) => {
  // console.log(
  //   'unpackFeatureData',
  //   properties ? properties.id : 'properties are empty'
  // )

  const values = Object.entries(properties)
    .map(([rawKey, value]) => {
      const key = camelCase(rawKey)

      if (!value || typeof value !== 'string') {
        return [key, value]
      }

      if (isEmpty(value)) {
        return [key, null]
      }

      if (key === 'name' || key === 'inputId') {
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

  // calculate area outside SE, rounded to 0 in case it is very small
  values.outsideSEPercent = (100 * values.outsideSe) / values.rasterizedAcres
  if (values.outsideSEPercent < 1) {
    values.outsideSEPercent = 0
  }

  // rescale scaled values from percent * 10 back to percent
  const priorityColumns = [
    'blueprint',
    'corridors',
    'base',
    'flm',
    'slrDepth',
    'slrNodata',
    'urban',
  ]
  priorityColumns.forEach((c) => {
    values[c] = values[c] ? applyFactor(values[c], 0.1) : []
  })

  // Transform Caribbean so that it follows same structure
  // It is dict-encoded percent*10
  // Array has positions 0 ... 24 to match possible priority values.
  if (values.car) {
    const car = Array.from(Array(25)).map(() => 0)
    Object.entries(values.car).forEach(([index, percent]) => {
      car[index] = percent / 10
    })
    values.car = car
  } else {
    values.car = []
  }

  // extract indicators where available
  values.indicators = {}

  if (values.baseIndicators) {
    values.indicators.base = extractIndicators(
      values.baseIndicators || {},
      ecosystemInfo,
      indicatorInfo.base.indicators,
      values.type
    )
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

  if (values.ltaSearch) {
    values.ltaSearch = values.ltaSearch.split(',').map((v) => parseFloat(v))
  } else {
    values.ltaSearch = null
  }

  // rename specific fields for easier use later
  values.unitType = values.type
  values.unitAcres = values.acres

  values.slr = {
    depth: values.slrDepth || [],
    nodata: values.slrNodata || [],
  }

  return values
}
