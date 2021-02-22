import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'
import { lighten } from '@theme-ui/color'

import { useBreakpoints } from 'components/layout'

import IndicatorAverageChart from './IndicatorAverageChart'
import { IndicatorPropType } from './proptypes'

const Indicator = ({ indicator, onSelect }) => {
  const { label, avg, domain } = indicator

  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

  const handleClick = useCallback(() => {
    onSelect(indicator)
  }, [indicator, onSelect])

  return (
    <Box
      onClick={handleClick}
      sx={{
        cursor: 'pointer',
        px: '1rem',
        pt: '1rem',
        pb: '2.5rem',
        position: 'relative',
        '&:hover': {
          bg: lighten('grey.0', 0.01),
          '& label': {
            display: 'block',
          },
        },
        '&:not(:first-of-type)': {
          borderTop: '2px solid',
          borderTopColor: 'grey.1',
        },
      }}
    >
      <Text
        sx={{
          color: 'primary',
          fontSize: 2,
          fontWeight: 'bold',
        }}
      >
        {label}
      </Text>

      <IndicatorAverageChart value={avg} domain={domain} />

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
    </Box>
  )
}

Indicator.propTypes = {
  type: PropTypes.string.isRequired,
  indicator: PropTypes.shape(IndicatorPropType).isRequired,
  onSelect: PropTypes.func.isRequired,
}

export default Indicator
