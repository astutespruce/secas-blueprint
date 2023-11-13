import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'
import { lighten } from '@theme-ui/color'

import { useBreakpoints } from 'components/layout'

import IndicatorPixelValueChart from './IndicatorPixelValueChart'
import { IndicatorPropType } from './proptypes'

const PixelIndicatorListItem = ({ indicator, onSelect }) => {
  const { label, values, valueLabel, goodThreshold } = indicator
  const present = indicator.total > 0
  const [currentValue] = values.filter(({ percent }) => percent === 100)
  const isZeroValue =
    !present || (currentValue.value === 0 && !currentValue.color)

  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

  const handleClick = useCallback(() => {
    onSelect(indicator)
  }, [indicator, onSelect])

  return (
    <Box
      onClick={present && !isZeroValue ? handleClick : undefined}
      sx={{
        cursor: present && !isZeroValue ? 'pointer' : 'unset',
        px: '1rem',
        pt: '1rem',
        pb: '1.5rem',
        position: 'relative',
        '&:not(:first-of-type)': {
          borderTop: '2px solid',
          borderTopColor: 'grey.1',
        },
        ...(present && !isZeroValue
          ? {
              '&:hover': {
                bg: lighten('grey.0', 0.01),
                '& label': {
                  display: 'block',
                },
              },
            }
          : {}),
      }}
    >
      <Text
        sx={{
          color: present && !isZeroValue ? 'primary' : 'grey.8',
          fontSize: 2,
          fontWeight: present && !isZeroValue ? 'bold' : 'unset',
        }}
      >
        {label}
      </Text>

      <Box>
        <IndicatorPixelValueChart
          present={present}
          values={values}
          currentValue={currentValue}
          isZeroValue={isZeroValue}
          valueLabel={valueLabel}
          goodThreshold={goodThreshold}
        />
      </Box>

      {present && !isZeroValue ? (
        <Text
          as="label"
          sx={{
            color: 'primary',
            fontSize: 'small',
            textAlign: 'center',
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            display: 'none',
          }}
        >
          {isMobile ? 'tap' : 'click'} for more details
        </Text>
      ) : null}
    </Box>
  )
}

PixelIndicatorListItem.propTypes = {
  indicator: PropTypes.shape(IndicatorPropType).isRequired,
  onSelect: PropTypes.func.isRequired,
}

export default PixelIndicatorListItem
