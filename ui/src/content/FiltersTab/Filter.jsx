import React, { useCallback, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Checkbox, Flex, Label, Text } from 'theme-ui'

import { InfoTooltip } from 'components/tooltip'
import { indexBy } from 'util/data'
import { useIsEqualCallback } from 'util/hooks'

const Filter = ({
  id,
  label,
  description,
  values,
  valueLabel: indicatorValueLabel,
  presenceLabel,
  enabled,
  activeValues,
  // goodThreshold, // TODO: implement or remove
  onChange,
}) => {
  const valueIndex = indexBy(values, 'value')
  const checkboxRef = useRef(null)
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

  // retain previous active values
  const toggleEnabled = useIsEqualCallback(() => {
    onChange({ id, enabled: !enabled, activeValues })

    // blur on uncheck
    if (checkboxRef.current && enabled) {
      checkboxRef.current.blur()
    }
  }, [id, enabled, activeValues, onChange])

  const handleToggleValue = (value) => () => {
    const newActiveValues = {
      ...activeValues,
    }

    // if a checkbox is a proxy for multiple values, toggle them all
    if (valueIndex[value].rawValues) {
      valueIndex[value].rawValues.forEach((v) => {
        newActiveValues[v] = !activeValues[v]
      })
    } else {
      newActiveValues[value] = !activeValues[value]
    }

    onChange({ id, enabled, activeValues: newActiveValues })
  }

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
              border: '2px solid transparent',
              '&:focus-within': {
                border: '2px dashed',
                borderColor: 'highlight',
              },
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
                'input:focus ~ &': {
                  backgroundColor: 'transparent',
                },
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
                        lineHeight: 1.3,
                        border: '2px solid transparent',
                        '&:focus-within': {
                          border: '2px dashed',
                          borderColor: 'highlight',
                        },
                      }}
                    >
                      <Checkbox
                        ref={checkboxRef}
                        readOnly={false}
                        checked={activeValues[value]}
                        onChange={handleToggleValue(value)}
                        sx={{
                          cursor: 'pointer',
                          mr: '0.25em',
                          width: '1.5em',
                          height: '1.5em',
                          'input:focus ~ &': {
                            backgroundColor: 'transparent',
                          },
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
  // goodThreshold: PropTypes.number,
  valueLabel: PropTypes.string,
  presenceLabel: PropTypes.string,
  activeValues: PropTypes.objectOf(PropTypes.bool).isRequired,
  enabled: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
}

Filter.defaultProps = {
  description: null,
  enabled: false,
  // goodThreshold: null,
  valueLabel: null,
  presenceLabel: null,
}

export default Filter
