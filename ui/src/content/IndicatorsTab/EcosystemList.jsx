import React, { useState, useCallback, memo } from 'react'
import PropTypes from 'prop-types'
import { dequal as deepEqual } from 'dequal'

import { flatten, indexBy } from 'util/data'
import { useIsEqualEffect } from 'util/hooks'

import Ecosystem from './Ecosystem'
import IndicatorDetails from './IndicatorDetails'
import { EcosystemPropType } from './proptypes'

const EcosystemList = ({ ecosystems, analysisAcres, blueprintAcres }) => {
  const indicators = flatten(
    Object.values(ecosystems).map(({ indicators: i }) => i)
  )
  const indicatorsIndex = indexBy(indicators, 'id')

  const [selectedIndicator, setSelectedIndicator] = useState(null)

  useIsEqualEffect(() => {
    if (selectedIndicator === null) {
      return
    }

    if (indicatorsIndex[selectedIndicator.id]) {
      setSelectedIndicator(() => indicatorsIndex[selectedIndicator.id])
    } else {
      // reset selected indicator, it isn't present in this set
      setSelectedIndicator(() => null)
    }
  }, [indicators])

  const handleSelectIndicator = useCallback((indicator) => {
    setSelectedIndicator(indicator)
  }, [])

  const handleCloseIndicator = useCallback(() => setSelectedIndicator(null), [])

  return (
    <>
      {selectedIndicator ? (
        <IndicatorDetails
          analysisAcres={analysisAcres}
          blueprintAcres={blueprintAcres}
          onClose={handleCloseIndicator}
          {...selectedIndicator}
        />
      ) : (
        ecosystems.map((ecosystem) => (
          <Ecosystem
            key={ecosystem.id}
            onSelectIndicator={handleSelectIndicator}
            {...ecosystem}
          />
        ))
      )}
    </>
  )
}

EcosystemList.propTypes = {
  analysisAcres: PropTypes.number.isRequired,
  blueprintAcres: PropTypes.number.isRequired,
  ecosystems: PropTypes.arrayOf(PropTypes.shape(EcosystemPropType)).isRequired,
}

export default memo(EcosystemList, (prev, next) => deepEqual(prev, next))
