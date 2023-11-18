import React from 'react'
import PropTypes from 'prop-types'
import { Flex, Box, Text, Progress } from 'theme-ui'

import { formatPercent } from 'util/format'

const IndicatorPercentChart = ({ label, percent, percentSuffix, color }) => (
  <Box sx={{ flex: '1 1 auto' }}>
    <Flex
      sx={{
        justifyContent: 'space-between',
        alignItems: 'flex-end',
        fontSize: 0,
      }}
    >
      <Text sx={{ flex: '1 1 auto' }}>{label}</Text>
      <Text
        sx={{
          color: 'grey.8',
          flex: '0 0 2.5rem',
          ml: '1em',
          textAlign: 'right',
        }}
      >
        {formatPercent(percent)}% {percentSuffix}
      </Text>
    </Flex>
    <Progress value={percent} max={100} color={color} />
  </Box>
)

IndicatorPercentChart.propTypes = {
  label: PropTypes.string.isRequired,
  percent: PropTypes.number.isRequired,
  percentSuffix: PropTypes.string,
  color: PropTypes.string,
}

IndicatorPercentChart.defaultProps = {
  percentSuffix: '',
  color: 'grey.8',
}

export default IndicatorPercentChart
