import React, { useState, useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { indexBy, flatten } from 'util/data'
import { useIsEqualLayoutEffect } from 'util/hooks'

import InputTabs from './InputTabs'
import Ecosystem from './Ecosystem'
import IndicatorDetails from './IndicatorDetails'

const IndicatorsTab = ({
  type,
  inputs: rawInputs,
  indicators: rawIndicators,
  outsideSEPercent,
  analysisAcres,
  blueprintAcres,
}) => {
  // index indicators by ID for lookup on selection
  const indicatorIndex = indexBy(
    flatten(
      Object.values(rawIndicators).map(({ indicators }) =>
        Object.values(indicators)
      )
    ),
    'id'
  )

  // merge ecosystems into input areas
  const inputs = rawInputs.map(({ id, ...rest }) => ({
    id,
    ...rest,
    ecosystems: rawIndicators[id] ? rawIndicators[id].ecosystems : [],
  }))
  const inputIndex = indexBy(inputs, 'id')

  const [selectedInput, setSelectedInput] = useState(
    rawInputs.length > 0 ? rawInputs[0].id : null
  )
  const [selectedIndicator, setSelectedIndicator] = useState(null)
  // update selected input for a new area
  useIsEqualLayoutEffect(() => {
    if (!inputIndex[selectedInput]) {
      setSelectedInput(rawInputs.length > 0 ? rawInputs[0].id : null)
    }
  }, [inputIndex, rawInputs])

  // Update selected indicator for a new area
  useIsEqualLayoutEffect(() => {
    if (selectedIndicator === null) {
      return
    }

    if (indicatorIndex[selectedIndicator.id]) {
      // Update the selected indicator if still available in the new area
      setSelectedIndicator({
        ...indicatorIndex[selectedIndicator.id],
        input: inputIndex[selectedIndicator.id.split(':')[0]],
      })
    } else {
      // reset selected indicator, it isn't present in this set
      setSelectedIndicator(() => null)
    }
  }, [rawIndicators])

  const handleSelectIndicator = useCallback(
    (indicator) => {
      // splice in input info
      setSelectedIndicator(
        indicator !== null
          ? { ...indicator, input: inputIndex[indicator.id.split(':')[0]] }
          : null
      )
    },
    [inputIndex]
  )

  const handleCloseIndicator = useCallback(() => setSelectedIndicator(null), [])

  if (selectedInput === null) {
    return (
      <Text sx={{ color: 'grey.8', textAlign: 'center' }}>
        No Blueprint inputs present in this area.
      </Text>
    )
  }

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

  if (selectedInput && inputIndex[selectedInput]) {
    const { ecosystems, label: inputLabel } = inputIndex[selectedInput]

    return (
      <>
        <InputTabs
          inputs={inputs}
          selectedInput={selectedInput}
          onSelectInput={setSelectedInput}
        />

        <Box>
          {ecosystems && ecosystems.length > 0 ? (
            <>
              {ecosystems.map((ecosystem) => (
                <Ecosystem
                  key={ecosystem.id}
                  type={type}
                  onSelectIndicator={handleSelectIndicator}
                  {...ecosystem}
                />
              ))}
            </>
          ) : (
            <Box sx={{ p: '1rem 2rem', color: 'grey.8', textAlign: 'center' }}>
              No indicators available for the {inputLabel} in this area.
            </Box>
          )}
        </Box>
      </>
    )
  }

  // this is just to hold the space until rerender for a new selectedInput
  return null
}

IndicatorsTab.propTypes = {
  type: PropTypes.string.isRequired,

  inputs: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
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
