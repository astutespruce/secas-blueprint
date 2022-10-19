import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph } from 'theme-ui'

import { useMapData } from 'components/data'
import { indexBy, flatten } from 'util/data'
import { useIsEqualEffect } from 'util/hooks'

import Ecosystem from './Ecosystem'
import IndicatorDetails from './IndicatorDetails'

const IndicatorsTab = ({
  type,
  inputId,
  indicators: indicatorsByInput,
  outsideSEPercent,
  rasterizedAcres,
}) => {
  const { selectedIndicator, setSelectedIndicator } = useMapData()

  // index indicators by ID for lookup on selection
  const indicatorsIndex = indexBy(
    flatten(
      Object.values(indicatorsByInput).map(({ indicators }) =>
        Object.values(indicators)
      )
    ),
    'id'
  )

  useIsEqualEffect(() => {
    if (!selectedIndicator) {
      return
    }

    if (!indicatorsIndex[selectedIndicator]) {
      // reset selected indicator, it isn't present in this set (outside valid ecosystems)
      setSelectedIndicator(null)
    }
  }, [indicatorsIndex, selectedIndicator])

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

  if (inputId !== 'base') {
    return (
      <Paragraph
        sx={{
          py: '2rem',
          px: '1rem',
          color: 'grey.7',
          textAlign: 'center',
          fontSize: 1,
        }}
      >
        No information on Blueprint indicators is available for this area.
      </Paragraph>
    )
  }

  if (selectedIndicator && indicatorsIndex[selectedIndicator]) {
    return (
      <IndicatorDetails
        type={type}
        outsideSEPercent={outsideSEPercent}
        rasterizedAcres={rasterizedAcres}
        onClose={handleCloseIndicator}
        {...indicatorsIndex[selectedIndicator]}
      />
    )
  }

  // Base Blueprint is only area that has indicators
  const {
    base: { ecosystems },
  } = indicatorsByInput

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
  inputId: PropTypes.string.isRequired,
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
    })
  ),
  outsideSEPercent: PropTypes.number,
  rasterizedAcres: PropTypes.number,
}

IndicatorsTab.defaultProps = {
  indicators: {},
  outsideSEPercent: 0,
  rasterizedAcres: 0,
}

export default IndicatorsTab
