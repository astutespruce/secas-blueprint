import rawBlueprint from 'blueprint.json'
import rawCorridors from 'corridors.json'
import ecosystems from 'ecosystems.json'
import rawIndicators from 'indicators.json'
import ownership from 'ownership.json'
import protection from 'protection.json'
import rawSLR from 'slr.json'
import subregions from 'subregions.json'
import urban from 'urban.json'

import { indexBy } from 'util/data'

// export unmodified values directly
export { ecosystems, ownership, protection, subregions, urban }

// Sort by descending value
export const blueprint = rawBlueprint.sort(
  ({ value: leftValue }, { value: rightValue }) =>
    rightValue > leftValue ? 1 : -1
)
// skip the first value
export const blueprintCategories = blueprint.slice(0, blueprint.length - 1)

// put 0 value at end
export const corridors = rawCorridors.slice(1).concat(rawCorridors.slice(0, 1))

// select subset of fields and add position within list
export const indicators = rawIndicators.map(
  (
    {
      id,
      label,
      url,
      description,
      goodThreshold,
      values,
      valueLabel,
      subregions: indicatorSubregions,
    },
    i
  ) => ({
    id,
    label,
    url,
    description,
    goodThreshold,
    values,
    valueLabel,
    subregions: new Set(indicatorSubregions),
    pos: i, // position within list of indicators, used to unpack packed indicator values
  })
)

// split depth and NODATA values
export const slrDepth = rawSLR.slice(0, 11)
export const slrNodata = rawSLR.slice(11)

export const subregionIndex = indexBy(subregions, 'value')
