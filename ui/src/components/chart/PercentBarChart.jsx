/** @jsxRuntime classic */
/** @jsx jsx */

// eslint-disable-next-line no-unused-vars
import React from 'react'
import PropTypes from 'prop-types'

import { Box, Flex, Progress, Text, jsx } from 'theme-ui'

import theme from 'theme'
import { formatPercent } from 'util/format'

const PercentBarChart = ({ label, percent, color, ...props }) => (
  <Box {...props}>
    <Flex
      sx={{
        justifyContent: 'space-between',
        fontSize: 1,
        flexWrap: 'nowrap',
        alignItems: 'flex-end',
      }}
    >
      <Text sx={{ flex: '1 1 auto', mr: '1em' }}>{label}</Text>
      <Text sx={{ color: 'grey.7', flex: '0 0 auto', fontSize: 0 }}>
        {formatPercent(percent)}% of area
      </Text>
    </Flex>
    <Progress
      variant="styles.progress.percent"
      value={percent}
      max={100}
      color={color}
    />
  </Box>
)

PercentBarChart.propTypes = {
  label: PropTypes.string.isRequired,
  percent: PropTypes.number.isRequired,
  color: PropTypes.string,
}

PercentBarChart.defaultProps = {
  color: theme.colors.primary,
}

export default PercentBarChart
