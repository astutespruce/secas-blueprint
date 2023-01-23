import React, { useMemo, useCallback, useRef } from 'react'
import PropTypes from 'prop-types'
import { Box, Checkbox, Label, Text } from 'theme-ui'

import { indexBy } from 'util/data'

import RangeSlider from './RangeSlider'

const IndicatorFilter = ({
  id,
  label,
  // description, // TODO: tooltip
  values,
  presenceLabel,
  enabled,
  range,
  goodThreshold,
  onChange,
}) => {
  const checkboxRef = useRef(null)

  const valueIndex = useMemo(() => indexBy(values, 'value'), [values])
  const hasRange = values[values.length - 1].value > values[0].value

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
        px: '1rem',
        py: '0.25rem',
        '&:not(:first-of-type)': {
          borderTop: '2px solid',
          borderTopColor: 'grey.1',
        },
      }}
    >
      <Box>
        <Label
          sx={{
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

        {enabled ? (
          <Box sx={{ ml: '1.75rem', mr: '1rem' }}>
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
              {hasRange
                ? `Showing: ${valueIndex[range[0]].label} to ${
                    valueIndex[range[1]].label
                  }`
                : `Showing: ${presenceLabel}`}
            </Text>
          </Box>
        ) : null}
      </Box>
    </Box>
  )
}

IndicatorFilter.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  // description: PropTypes.string.isRequired,
  values: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  goodThreshold: PropTypes.number,
  presenceLabel: PropTypes.string,
  range: PropTypes.arrayOf(PropTypes.number).isRequired,
  enabled: PropTypes.bool,
  onChange: PropTypes.func,
}

IndicatorFilter.defaultProps = {
  enabled: false,
  goodThreshold: null,
  presenceLabel: null,
  onChange: () => {},
}

export default IndicatorFilter
