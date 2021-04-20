import React from 'react'
import PropTypes from 'prop-types'
import { Flex, Box, Text, Progress } from 'theme-ui'

import { formatPercent } from 'util/format'

const IndicatorPercentChart = ({
  value,
  label,
  percent,
  percentSuffix,
  color,
}) => (
  <Box sx={{ flex: '1 1 auto' }}>
    <Flex
      sx={{
        justifyContent: 'space-between',
        alignItems: 'flex-end',
        fontSize: 0,
      }}
    >
      <Text sx={{ flex: '1 1 auto' }}>{label}</Text>
      <Text sx={{ color: 'grey.6', flex: '0 0 auto', ml: '1em' }}>
        {formatPercent(percent)}% {percentSuffix}
      </Text>
    </Flex>
    <Progress value={percent} max={100} color={color} />
  </Box>
)

IndicatorPercentChart.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]), // if null, is remainder value
  label: PropTypes.string.isRequired,
  percent: PropTypes.number.isRequired,
  percentSuffix: PropTypes.string,
  color: PropTypes.string,
}

IndicatorPercentChart.defaultProps = {
  value: null,
  percentSuffix: '',
  color: 'grey.8',
}

export default IndicatorPercentChart
