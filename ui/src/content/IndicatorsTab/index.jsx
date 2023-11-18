import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { useMapData } from 'components/data'
import { useIsEqualEffect } from 'util/hooks'

import Ecosystem from './Ecosystem'
import IndicatorDetails from './IndicatorDetails'

const IndicatorsTab = ({
  type,
  indicators: { indicators, ecosystems },
  outsideSEPercent,
  rasterizedAcres,
}) => {
  const { selectedIndicator, setSelectedIndicator } = useMapData()

  useIsEqualEffect(() => {
    if (!selectedIndicator) {
      return
    }

    if (!indicators[selectedIndicator]) {
      // reset selected indicator, it isn't present in this set (outside valid ecosystems)
      setSelectedIndicator(null)
    }
  }, [indicators, selectedIndicator])

  const handleSelectIndicator = useCallback(
    (indicator) => {
      setSelectedIndicator(indicator.id)
    },
    [setSelectedIndicator]
  )

  const handleCloseIndicator = useCallback(
    () => setSelectedIndicator(null),
    [setSelectedIndicator]
  )

  if (selectedIndicator && indicators[selectedIndicator]) {
    return (
      <IndicatorDetails
        type={type}
        outsideSEPercent={outsideSEPercent}
        rasterizedAcres={rasterizedAcres}
        onClose={handleCloseIndicator}
        {...indicators[selectedIndicator]}
      />
    )
  }

  return (
    <Box>
      {ecosystems.map((ecosystem) => (
        <Ecosystem
          key={ecosystem.id}
          type={type}
          onSelectIndicator={handleSelectIndicator}
          {...ecosystem}
        />
      ))}
    </Box>
  )
}

IndicatorsTab.propTypes = {
  type: PropTypes.string.isRequired,
  indicators: PropTypes.shape({
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
        url: PropTypes.string,
        continuous: PropTypes.bool,
        domain: PropTypes.arrayOf(PropTypes.number),
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
  }),
  outsideSEPercent: PropTypes.number,
  rasterizedAcres: PropTypes.number,
}

IndicatorsTab.defaultProps = {
  indicators: {},
  outsideSEPercent: 0,
  rasterizedAcres: 0,
}

export default IndicatorsTab
