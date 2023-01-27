import React, { useCallback, useRef } from 'react'
import PropTypes from 'prop-types'
import { Box, Checkbox, Flex, Label, Text } from 'theme-ui'

import { InfoTooltip } from 'components/tooltip'
import { indexBy } from 'util/data'

import RangeSlider from './RangeSlider'

const Filter = ({
  id,
  label,
  description,
  values,
  valueLabel,
  presenceLabel,
  enabled,
  range,
  goodThreshold,
  onChange,
}) => {
  const checkboxRef = useRef(null)

  const hasRange = values[values.length - 1].value > values[0].value
  const valueIndex = indexBy(values, 'value')

  let summaryLabel = null
  if (hasRange) {
    if (range[1] > range[0]) {
      summaryLabel = `Showing: ${valueIndex[range[0]].label} to ${
        valueIndex[range[1]].label
      }`
    } else {
      summaryLabel = `Showing: ${valueIndex[range[0]].label}`
    }
  } else {
    summaryLabel = `Showing: ${presenceLabel} (presence-only indicator)`
  }

  const tooltipContent = (
    <Box sx={{ fontSize: 0 }}>
      <Text sx={{ mb: 0, fontSize: 1, fontWeight: 'bold' }}>{label}</Text>
      {description ? <Text sx={{ mb: '0.5rem' }}>{description}</Text> : null}
      <b>{valueLabel || 'Values'}:</b>
      <br />
      {hasRange ? (
        <Box
          as="ul"
          sx={{
            m: 0,
            lineHeight: 1.2,
            fontSize: 0,
            '& li+li': {
              mt: '0.25em',
            },
          }}
        >
          {values.map(
            ({ value, label: valueLabel, description: valueDescription }) => (
              <li key={value}>
                {valueLabel}
                {valueDescription ? `: ${valueDescription}` : null}
              </li>
            )
          )}
        </Box>
      ) : (
        `${presenceLabel} (presence-only indicator)`
      )}
    </Box>
  )

  // retain existing range when toggling enabled
  const toggleEnabled = useCallback(() => {
    onChange({ id, enabled: !enabled, range })

    // blur on uncheck
    if (checkboxRef.current && enabled) {
      checkboxRef.current.blur()
    }
  }, [id, enabled, range, onChange])

  const handleRangeChange = useCallback(
    (newRange) => {
      onChange({ id, enabled: true, range: newRange })
    },
    [id, onChange]
  )

  return (
    <Box
      sx={{
        pl: '1rem',
        pr: '0.5rem',
        py: '0.25rem',
        '&:not(:first-of-type)': {
          borderTop: '2px solid',
          borderTopColor: 'grey.1',
        },
      }}
    >
      <Box>
        <Flex sx={{ justifyContent: 'space-between', alignItems: 'center' }}>
          <Label
            sx={{
              flex: '1 1 auto',
              fontSize: 1,
              fontWeight: enabled ? 'bold' : 'normal',
              lineHeight: 1.5,
            }}
          >
            <Checkbox
              ref={checkboxRef}
              readOnly={false}
              checked={enabled}
              onChange={toggleEnabled}
              sx={{
                cursor: 'pointer',
                mr: '0.25em',
                width: '1.5em',
                height: '1.5em',
              }}
            />

            {label}
          </Label>

          <InfoTooltip content={tooltipContent} direction="right">
            <Flex
              sx={{
                flex: '0 0 auto',
                ml: '0.5em',
                justifyContent: 'center',
                alignItems: 'center',
                height: '1.5em',
                width: '1.5em',
                borderRadius: '2em',
                border: '1px solid',
                borderColor: 'grey.3',
                '&:hover': {
                  bg: 'grey.1',
                  borderColor: 'grey.4',
                },
              }}
            >
              i
            </Flex>
          </InfoTooltip>
        </Flex>

        {enabled ? (
          <Box sx={{ ml: '1.75rem', mr: '1rem' }}>
            {valueLabel ? (
              <Text sx={{ fontSize: 0, color: 'grey.8' }}>{valueLabel}</Text>
            ) : null}
            {hasRange ? (
              <RangeSlider
                values={values}
                range={range}
                goodThreshold={goodThreshold}
                onChange={handleRangeChange}
              />
            ) : null}

            <Text
              sx={{
                fontSize: 0,
                color: 'grey.8',
                pb: '0.5rem',
              }}
            >
              {summaryLabel}
            </Text>
          </Box>
        ) : null}
      </Box>
    </Box>
  )
}

Filter.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  description: PropTypes.string,
  values: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  goodThreshold: PropTypes.number,
  valueLabel: PropTypes.string,
  presenceLabel: PropTypes.string,
  range: PropTypes.arrayOf(PropTypes.number).isRequired,
  enabled: PropTypes.bool,
  onChange: PropTypes.func,
}

Filter.defaultProps = {
  description: null,
  enabled: false,
  goodThreshold: null,
  valueLabel: null,
  presenceLabel: null,
  onChange: () => {},
}

export default Filter
