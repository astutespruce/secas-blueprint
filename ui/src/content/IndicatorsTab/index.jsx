import React, { useState, useCallback } from 'react'
import PropTypes from 'prop-types'

import { indexBy, flatten } from 'util/data'
import { useIsEqualEffect } from 'util/hooks'

import InputAreas from './InputAreas'
import IndicatorDetails from './IndicatorDetails'

const IndicatorsTab = ({
  type,
  inputs,
  indicators: rawIndicators,
  outsideSEPercent,
  analysisAcres,
  blueprintAcres,
}) => {
  console.log('incoming inputs', inputs)
  console.log('incoming indicators', rawIndicators)

  // const [selectedIndicator, setSelectedIndicator] = useState(null)

  // FIXME:
  const [selectedIndicator, setSelectedIndicator] = useState(
    Object.values(rawIndicators.sa.indicators)[0]
  )

  console.log(
    'indicators for each input',
    Object.values(rawIndicators).map(({ indicators }) => indicators)
  )

  const indicatorIndex = indexBy(
    flatten(
      Object.values(rawIndicators).map(({ indicators }) =>
        Object.values(indicators)
      )
    ),
    'id'
  )

  console.log('indicatorIndex', indicatorIndex)

  useIsEqualEffect(() => {
    if (selectedIndicator === null) {
      return
    }

    if (indicatorIndex[selectedIndicator.id]) {
      setSelectedIndicator(() => indicatorIndex[selectedIndicator.id])
    } else {
      // reset selected indicator, it isn't present in this set
      setSelectedIndicator(() => null)
    }
  }, [rawIndicators])

  const handleSelectIndicator = useCallback((indicator) => {
    setSelectedIndicator(indicator)
  }, [])

  const handleCloseIndicator = useCallback(() => setSelectedIndicator(null), [])

  if (selectedIndicator) {
    return (
      <IndicatorDetails
        type={type}
        outsideSEPercent={outsideSEPercent}
        analysisAcres={analysisAcres}
        blueprintAcres={blueprintAcres}
        onClose={handleCloseIndicator}
        {...selectedIndicator}
      />
    )
  }

  return <InputAreas inputs={inputs} indicators={rawIndicators} />
}

IndicatorsTab.propTypes = {
  type: PropTypes.string.isRequired,

  inputs: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      percent: PropTypes.number.isRequired,
    })
  ),
  indicators: PropTypes.objectOf(
    PropTypes.shape({
      ecosystems: PropTypes.arrayOf(
        PropTypes.shape({
          id: PropTypes.string.isRequired,
          color: PropTypes.string.isRequired,
          indicators: PropTypes.arrayOf(PropTypes.object), // same structure as indicators below
        })
      ),
      indicators: PropTypes.objectOf(
        PropTypes.shape({
          id: PropTypes.string.isRequired,
          label: PropTypes.string.isRequired,
          description: PropTypes.string,
          datasetID: PropTypes.string,
          continuous: PropTypes.bool,
          domain: PropTypes.arrayOf(PropTypes.number),
          units: PropTypes.string,
          percent: PropTypes.arrayOf(PropTypes.number),
          goodThreshold: PropTypes.number,
          values: PropTypes.arrayOf(
            PropTypes.shape({
              value: PropTypes.number.isRequired,
              label: PropTypes.string.isRequired,
              percent: PropTypes.number,
            })
          ),
        })
      ),
    })
  ),
  outsideSEPercent: PropTypes.number,
  analysisAcres: PropTypes.number,
  blueprintAcres: PropTypes.number,
}

IndicatorsTab.defaultProps = {
  inputs: [],
  indicators: {},
  outsideSEPercent: 0,
  analysisAcres: 0,
  blueprintAcres: 0,
}

export default IndicatorsTab
