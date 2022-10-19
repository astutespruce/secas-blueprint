import React, { useState, useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { OutboundLink } from 'components/link'
import { useMapData } from 'components/data'
import { indexBy, flatten } from 'util/data'
import { useIsEqualLayoutEffect, useIsEqualEffect } from 'util/hooks'

import InputTabs from './InputTabs'
import Ecosystem from './Ecosystem'
import IndicatorDetails from './IndicatorDetails'

const IndicatorsTab = ({
  type,
  inputs: rawInputs,
  indicators: rawIndicators,
  outsideSEPercent,
  rasterizedAcres,
}) => {
  const { selectedIndicator, setSelectedIndicator } = useMapData()

  // index indicators by ID for lookup on selection
  const indicatorsIndex = indexBy(
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

  // const [selectedIndicator, setSelectedIndicator] = useState(null)

  // update selected input for a new area
  useIsEqualLayoutEffect(() => {
    if (!inputIndex[selectedInput]) {
      setSelectedInput(rawInputs.length > 0 ? rawInputs[0].id : null)
    }
  }, [inputIndex, rawInputs])

  // // Update selected indicator for a new area
  // useIsEqualLayoutEffect(() => {
  //   if (selectedIndicator === null) {
  //     return
  //   }

  //   if (indicatorsIndex[selectedIndicator.id]) {
  //     // Update the selected indicator if still available in the new area
  //     setSelectedIndicator({
  //       ...indicatorsIndex[selectedIndicator.id],
  //       input: inputIndex[selectedIndicator.id.split(':')[0]],
  //     })
  //   } else {
  //     // reset selected indicator, it isn't present in this set
  //     setSelectedIndicator(() => null)
  //   }
  // }, [rawIndicators])

  // const handleSelectIndicator = useCallback(
  //   (indicator) => {
  //     // splice in input info
  //     setSelectedIndicator(
  //       indicator !== null
  //         ? { ...indicator, input: inputIndex[indicator.id.split(':')[0]] }
  //         : null
  //     )
  //   },
  //   [inputIndex]
  // )

  // const handleCloseIndicator = useCallback(() => setSelectedIndicator(null), [])

  useIsEqualEffect(() => {
    if (!selectedIndicator) {
      return
    }

    if (!indicatorsIndex[selectedIndicator]) {
      // reset selected indicator, it isn't present in this set (outside valid ecosystems or input area)
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

  if (selectedInput === null) {
    return (
      <Text sx={{ color: 'grey.8', textAlign: 'center' }}>
        No Blueprint inputs present in this area.
      </Text>
    )
  }

  if (selectedIndicator && indicatorsIndex[selectedIndicator]) {
    return (
      <IndicatorDetails
        type={type}
        outsideSEPercent={outsideSEPercent}
        rasterizedAcres={rasterizedAcres}
        onClose={handleCloseIndicator}
        input={inputIndex[selectedIndicator.split(':')[0]]}
        {...indicatorsIndex[selectedIndicator]}
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
            <Box sx={{ p: '1rem 2rem', color: 'grey.8' }}>
              Indicator data are not available in this tool for {inputLabel}.
              Additional underlying data for this Blueprint input may be
              available{' '}
              <OutboundLink to={inputIndex[selectedInput].dataURL}>
                here
              </OutboundLink>
              .
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
  inputs: [],
  indicators: {},
  outsideSEPercent: 0,
  rasterizedAcres: 0,
}

export default IndicatorsTab
