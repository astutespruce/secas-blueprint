import camelCase from 'camelcase'

import {
  applyFactor,
  parsePipeEncodedValues,
  parseDeltaEncodedValues,
  parseDictEncodedValues,
  indexBy,
  setIntersection,
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
 * @param {Array} ecosystemInfo - array of ecosystem info
 * @param {Array} indicatorInfo - array of indicator info
 * @param {Array} subregions - array of subregion names
 */
const extractIndicators = (
  packedPercents,
  ecosystemInfo,
  indicatorInfo,
  subregions
) => {
  const ecosystemIndex = indexBy(ecosystemInfo, 'id')

  // merge incoming packed percents with indicator info
  let indicators = indicatorInfo
    // only show indicators that are either present or likely present based on
    // subregion
    .filter(({ subregions: indicatorSubregions }, i) => {
      const present = !!packedPercents[i]

      return (
        present || setIntersection(indicatorSubregions, subregions).size > 0
      )
    })
    .map(({ pos, values: valuesInfo, ...indicator }) => {
      const present = !!packedPercents[pos]

      const percents = present ? applyFactor(packedPercents[pos], 0.1) : []

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
        ecosystem: ecosystemIndex[indicator.id.split('_')[0]],
      }
    })

  // aggregate these up by ecosystems for ecosystems that are present
  const ecosystemsPresent = new Set(
    indicators
      .filter(({ values }) => sum(values.map(({ percent }) => percent)) > 0)
      .map(({ ecosystem: { id } }) => id)
  )

  indicators = indexBy(indicators, 'id')

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
 * @param {Object} properties
 * @param {Array} ecosystemInfo - array of ecosystem info
 * @param {Array} indicatorInfo - array of indicator info
 * @param {Object} subregionIndex - lookup of subregions by value
 */
export const unpackFeatureData = (
  properties,
  ecosystemInfo,
  indicatorInfo,
  subregionIndex
) => {
  const values = Object.entries(properties)
    .map(([rawKey, value]) => {
      const key = camelCase(rawKey)

      if (!value || typeof value !== 'string' || key === 'name') {
        return [key, value]
      }

      if (isEmpty(value)) {
        return [key, null]
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

      // everything else
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
  const scaledColumns = [
    'blueprint',
    'corridors',
    'ownership',
    'slrDepth',
    'slrNodata',
    'urban',
    'wildfireRisk',
  ]
  scaledColumns.forEach((c) => {
    values[c] = values[c] ? applyFactor(values[c], 0.1) : []
  })

  values.subregions = new Set(
    (values.subregions || '').split(',').map((v) => subregionIndex[v].subregion)
  )

  values.indicators = extractIndicators(
    values.indicators || {},
    ecosystemInfo,
    indicatorInfo,
    values.subregions
  )

  // rename specific fields for easier use later
  values.unitType = values.type
  values.unitAcres = values.acres

  values.slr = {
    depth: values.slrDepth || [],
    nodata: values.slrNodata || [],
  }

  return values
}
