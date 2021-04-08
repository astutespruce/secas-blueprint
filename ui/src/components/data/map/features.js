import {
  applyFactor,
  parsePipeEncodedValues,
  parseDeltaEncodedValues,
  parseDictEncodedValues,
  indexBy,
  sortByFuncMultiple,
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
      const values = valuesInfo.map(({ value, ...valueInfo }) => ({
        value,
        ...valueInfo,
        percent: present ? percents[value] : 0,
      }))

      return {
        percent: percents,
        ...indicator,
        values,
        total: sum(values.map(({ percent: p }) => p)),
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
 * @param {Object} inputValues - mapping of index to input ID
 * @param {Object} inputInfo - lookup of input area info by input area id
 * @param {Object} ecosystemInfo - array of ecosystem info
 * @param {Object} indicatorValues - mapping of index in input to indicator object
 */
export const unpackFeatureData = (
  properties,
  inputValues,
  inputInfo,
  ecosystemInfo,
  indicatorInfo
) => {
  console.log(
    'unpackFeatureData',
    properties ? properties.id : 'properties are empty'
  )
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

  // calculate area outside SE, rounded to 0 in case it is very small
  values.outsideSEPercent = 100 - sum(values.blueprint)
  if (values.outsideSEPercent < 1) {
    values.outsideSEPercent = 0
  }

  values.gulf_hypoxia = values.gulf_hypoxia
    ? applyFactor(values.gulf_hypoxia, 0.1)
    : []

  values.fl_blueprint = values.fl_blueprint
    ? applyFactor(values.fl_blueprint, 0.1)
    : []

  values.flm_blueprint = values.flm_blueprint
    ? applyFactor(values.flm_blueprint, 0.1)
    : []

  values.midse_blueprint = values.midse_blueprint
    ? applyFactor(values.midse_blueprint, 0.1)
    : []

  values.nn_priority = values.nn_priority
    ? applyFactor(values.nn_priority, 0.1)
    : []

  values.ns_priority = values.ns_priority
    ? applyFactor(values.ns_priority, 0.1)
    : []

  values.okchatrank = values.okchatrank
    ? applyFactor(values.okchatrank, 0.1)
    : []

  values.txchatrank = values.txchatrank
    ? applyFactor(values.txchatrank, 0.1)
    : []

  values.sa_blueprint = values.sa_blueprint
    ? applyFactor(values.sa_blueprint, 0.1)
    : []

  // Transform Caribbean so that it follows same structure
  // it will be 100% of whichever rank it is assigned; this will be
  // corrected when used based on the amount of overlap with this input area.
  // Array has positions 0 ... 24 to match possible priority values.
  const carPercent = Array.from(Array(25)).map(() => 0)
  if (values.carrank !== null && values.carrank !== undefined) {
    carPercent[values.carrank] = 100
    values.carrank = carPercent
  } else {
    values.carrank = []
  }

  // flatten inputs
  let hasInputOverlaps = false
  const flatInputs = {}
  values.inputs.forEach((percent, i) => {
    if (percent === 0) {
      // we need i to map to the correct inputId, so we can't filter 0 percents
      // out in advance
      return
    }
    const inputIds = inputValues[i].split(',')
    if (inputIds.length > 1) {
      hasInputOverlaps = true
    }
    inputIds.forEach((id) => {
      if (!flatInputs[id]) {
        flatInputs[id] = { id, percent }
      } else {
        flatInputs[id].percent += percent
      }
    })
  })

  values.inputs = Object.values(flatInputs)
    .map(({ id, percent }) => ({
      id,
      percent,
      ...inputInfo[id],
    }))
    .sort(
      sortByFuncMultiple([
        { field: 'percent', ascending: false },
        { field: 'label', ascending: true },
      ])
    )
  values.hasInputOverlaps = hasInputOverlaps

  // extract indicators where available
  values.indicators = {}
  if (values.fl_indicators) {
    values.indicators.fl = extractIndicators(
      values.fl_indicators || {},
      ecosystemInfo,
      indicatorInfo.fl.indicators,
      values.type
    )
  }

  if (values.flm_indicators) {
    values.indicators.flm = extractIndicators(
      values.flm_indicators || {},
      ecosystemInfo,
      indicatorInfo.flm.indicators,
      values.type
    )
  }

  if (values.nn_indicators) {
    values.indicators.nn = extractIndicators(
      values.nn_indicators || {},
      ecosystemInfo,
      indicatorInfo.nn.indicators,
      values.type
    )
  }

  if (values.sa_indicators) {
    values.indicators.sa = extractIndicators(
      values.sa_indicators || {},
      ecosystemInfo,
      indicatorInfo.sa.indicators,
      values.type
    )
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

  return values
}
