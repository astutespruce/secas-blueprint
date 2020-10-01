import React from 'react'
import PropTypes from 'prop-types'

import { useIndicators } from 'components/data'
import { indexBy, sum, percentsToAvg } from 'util/data'

import EcosystemList from './EcosystemList'

const IndicatorsTab = ({
  indicators: rawIndicators,
  analysisAcres,
  blueprintAcres,
}) => {
  const { ecosystems: ECOSYSTEMS, indicators: INDICATORS } = useIndicators()

  // retrieve indicator results by original index
  const indicators = indexBy(
    INDICATORS.map((indicator, i) => ({
      ...indicator,
      index: i,
    }))
      .filter((_, i) => rawIndicators[i] !== undefined)
      .map(({ index, ...indicator }) => {
        const { percent, avg = null } = rawIndicators[index]

        const values = indicator.values.map(({ value, ...rest }) => ({
          value,
          ...rest,
          percent: percent[value],
        }))

        return {
          ...indicator,
          index,
          values,
          // calculate average based on the values that are present
          // if values do not start at 1
          avg:
            avg !== null
              ? avg
              : percentsToAvg(values.map(({ percent: p }) => p)) +
                values[0].value,
          total: sum(values.map(({ percent: p }) => p)),
        }
      })
      // Only include those that have nonzero values
      .filter(({ total }) => total > 0),
    'id'
  )

  const ecosystemsPresent = new Set(
    Object.keys(indicators).map((id) => id.split('_')[0])
  )

  // Aggregate ecosystems and indicators into a nested data structure
  // ONLY for ecosystems that have indicators present
  const ecosystems = ECOSYSTEMS.filter(({ id }) =>
    ecosystemsPresent.has(id)
  ).map(
    ({
      id: ecosystemId,
      label,
      color,
      borderColor,
      indicators: ecosystemIndicators,
      ...rest
    }) => {
      const indicatorsPresent = ecosystemIndicators
        .map((indicatorId) => `${ecosystemId}_${indicatorId}`)
        .filter((indicatorId) => indicators[indicatorId])

      return {
        ...rest,
        id: ecosystemId,
        label,
        color,
        borderColor,
        indicators: indicatorsPresent.map((indicatorId) => ({
          ...indicators[indicatorId],
          ecosystem: {
            id: ecosystemId,
            label,
            color,
            borderColor,
          },
        })),
      }
    }
  )

  return (
    <EcosystemList
      ecosystems={ecosystems}
      analysisAcres={analysisAcres}
      blueprintAcres={blueprintAcres}
    />
  )
}

IndicatorsTab.propTypes = {
  analysisAcres: PropTypes.number.isRequired,
  blueprintAcres: PropTypes.number.isRequired,
  // NOTE: indicators are keyed by index not id
  indicators: PropTypes.objectOf(
    PropTypes.shape({
      percent: PropTypes.arrayOf(PropTypes.number).isRequired,
      avg: PropTypes.number,
    })
  ).isRequired,
}

export default IndicatorsTab
