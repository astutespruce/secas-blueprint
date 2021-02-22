import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

const labelCSS = {
  color: 'grey.6',
  fontSize: 0,
  flex: '0 0 auto',
}

const IndicatorAverageChart = ({ value, domain }) => {
  const [minValue, maxValue] = domain
  const percent = (100 * (value - minValue)) / (maxValue - minValue)

  return (
    <Flex sx={{ alignItems: 'center', mt: '0.5rem' }}>
      <Text sx={labelCSS}>Low</Text>
      <Box
        sx={{
          flex: '1 1 auto',
          width: '100%',
          position: 'relative',
          zIndex: 1,
          mx: '1rem',
          height: '2px',
          bg: 'grey.3',
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            borderRadius: '2em',
            height: '1.5em',
            width: '1.5em',
            left: `${percent}%`,
            ml: '-.75em',
            bg: 'grey.8',
            top: '-0.75em',
          }}
        />
        <Text
          sx={{
            position: 'absolute',
            left: `${percent}%`,
            fontSize: '10px',
            color: 'grey.8',
            top: '1em',
            ml: '-0.9em',
          }}
        >
          avg
        </Text>
      </Box>
      <Text sx={labelCSS}>High</Text>
    </Flex>
  )
}

IndicatorAverageChart.propTypes = {
  value: PropTypes.number.isRequired,
  domain: PropTypes.arrayOf(PropTypes.number).isRequired,
}

export default IndicatorAverageChart
