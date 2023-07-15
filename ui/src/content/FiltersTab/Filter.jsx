import React, { useCallback, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Checkbox, Flex, Label, Text } from 'theme-ui'

import { InfoTooltip } from 'components/tooltip'

const Filter = ({
  id,
  label,
  description,
  values,
  valueLabel: indicatorValueLabel,
  presenceLabel,
  enabled,
  range,
  goodThreshold,
  onChange,
}) => {
  const checkboxRef = useRef(null)

  // NOTE: this is clunky and does not update
  const [valueState, setValueState] = useState(() =>
    Object.fromEntries(
      values.map(({ value }) => [value, value >= range[0] && value <= range[1]])
    )
  )

  const hasMultipleValues = values.length > 1

  const tooltipContent = (
    <Box sx={{ fontSize: 0 }}>
      <Text sx={{ mb: 0, fontSize: 1, fontWeight: 'bold' }}>{label}</Text>
      {description ? <Text sx={{ mb: '0.5rem' }}>{description}</Text> : null}
      <b>{indicatorValueLabel || 'Values'}:</b>
      <br />
      {hasMultipleValues ? (
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

  const handleValueCheckboxChange = useCallback(
    (value) => () => {
      setValueState((prevState) => {
        const newState = {
          ...prevState,
          [value]: !prevState[value],
        }

        // FIXME: temporary hack until backend is updated
        const enabledValues = Object.entries(newState)
          .filter(([k, v]) => v)
          .map(([k, v]) => k)
        onChange({
          id,
          enabled: true,
          range: [Math.min(...enabledValues), Math.max(...enabledValues)],
        })
        return newState
      })
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

          <InfoTooltip content={tooltipContent} direction="right" />
        </Flex>

        {enabled ? (
          <Box sx={{ ml: '1.75rem', mr: '1rem' }}>
            {indicatorValueLabel ? (
              <Text sx={{ fontSize: 0, color: 'grey.8', lineHeight: 1.2 }}>
                {indicatorValueLabel}
              </Text>
            ) : null}
            {hasMultipleValues ? (
              <Box sx={{ mt: '0.25rem' }}>
                {values.map(({ value, label: valueLabel }) => (
                  <Box key={value}>
                    <Label
                      sx={{
                        flex: '1 1 auto',
                        fontSize: 1,
                        // TODO:
                        // fontWeight: enabled ? 'bold' : 'normal',
                        lineHeight: 1.5,
                      }}
                    >
                      <Checkbox
                        ref={checkboxRef}
                        readOnly={false}
                        checked={valueState[value]}
                        onChange={handleValueCheckboxChange(value)}
                        sx={{
                          cursor: 'pointer',
                          mr: '0.25em',
                          width: '1.5em',
                          height: '1.5em',
                        }}
                      />

                      {valueLabel}
                    </Label>
                  </Box>
                ))}
              </Box>
            ) : (
              <Text
                sx={{
                  fontSize: 0,
                  color: 'grey.8',
                  pb: '0.5rem',
                  lineHeight: 1.2,
                }}
              >
                {/* {summaryLabel} */}
                Showing: {presenceLabel} (presence-only indicator)
              </Text>
            )}
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
