import React, { useCallback, useRef } from 'react'
import PropTypes from 'prop-types'
import { Box, Checkbox, Flex, Label, Text } from 'theme-ui'
import { Filter as FilterIcon, Plus } from '@emotion-icons/fa-solid'

import { InfoTooltip } from 'components/tooltip'
import { indexBy } from 'util/data'
import { useIsEqualCallback } from 'util/hooks'

const Filter = ({
  id,
  label,
  description,
  values,
  valueLabel: indicatorValueLabel,
  enabled,
  activeValues,
  // goodThreshold, // TODO: implement or remove
  onChange,
}) => {
  const valueIndex = indexBy(values, 'value')
  const checkboxRef = useRef(null)

  const tooltipContent = (
    <Box sx={{ fontSize: 0 }}>
      <Text sx={{ mb: 0, fontSize: 1, fontWeight: 'bold' }}>{label}</Text>
      {description ? (
        <Text sx={{ mb: '0.5rem' }}>
          {/* handle links */}
          {description.search(/<a/g) !== -1 ? (
            <div dangerouslySetInnerHTML={{ __html: description }} />
          ) : (
            description
          )}
        </Text>
      ) : null}
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

  const handleKeyDown = useCallback(
    ({ key }) => {
      if (key === 'Enter' || key === ' ') {
        onChange({ id, enabled: !enabled, activeValues })
      }
    },
    [id, enabled, activeValues, onChange]
  )

  return (
    <Box
      sx={{
        pr: '0.5rem',
        '&:hover': {
          borderColor: 'highlight',
          '& .filter-icon': {
            color: 'grey.9',
          },
          '& .label': {
            bg: 'blue.0',
          },
        },
        '&:not(:first-of-type)': {
          borderTop: '2px solid',
          borderTopColor: 'grey.1',
        },
      }}
    >
      <Box>
        <Flex sx={{ justifyContent: 'space-between', alignItems: 'center' }}>
          <Box
            tabIndex={0}
            onClick={toggleEnabled}
            onKeyDown={handleKeyDown}
            className="label"
            sx={{
              flex: '1 1 auto',
              pl: '1rem',
              py: '0.25rem',
              fontSize: 1,
              fontWeight: enabled ? 'bold' : 'normal',
              lineHeight: 1.5,
              border: '2px solid transparent',
              cursor: 'pointer',
              '&:focus-within': {
                border: '2px dashed',
                borderColor: 'highlight',
              },
            }}
          >
            <Flex
              sx={{
                flex: '1 1 auto',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <Box
                className="filter-icon"
                sx={{ color: enabled ? 'grey.9' : 'grey.4' }}
              >
                {enabled ? (
                  <Box
                    sx={{
                      position: 'relative',
                    }}
                  >
                    <FilterIcon
                      size="1em"
                      style={{ position: 'relative', top: 0 }}
                    />
                  </Box>
                ) : (
                  <Box sx={{ position: 'relative' }}>
                    <FilterIcon size="1em" style={{ top: 0 }} />
                    <Text
                      sx={{
                        position: 'absolute',
                        top: '-0.2rem',
                        left: '-0.5rem',
                        fontSize: 3,
                        fontWeight: 'bold',
                      }}
                    >
                      <Plus size="0.6em" />
                    </Text>
                  </Box>
                )}
              </Box>
              <Text>{label}</Text>
            </Flex>
          </Box>

          <InfoTooltip content={tooltipContent} direction="right" />
        </Flex>

        {enabled ? (
          <Box sx={{ ml: '2.5rem', mr: '1rem', pb: '0.5rem' }}>
            <Box>
              {indicatorValueLabel ? (
                <Text sx={{ lineHeight: 1.2, mb: '0.5rem' }}>
                  {indicatorValueLabel}:
                </Text>
              ) : null}

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
  activeValues: PropTypes.objectOf(PropTypes.bool).isRequired,
  enabled: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
}

Filter.defaultProps = {
  description: null,
  enabled: false,
  // goodThreshold: null,
  valueLabel: null,
}

export default Filter
