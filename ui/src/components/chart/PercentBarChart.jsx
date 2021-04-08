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
        opacity: percent > 0 ? 1 : 0.5,
      }}
    >
      <Text
        sx={{
          flex: '1 1 auto',
          mr: '1em',
          color: percent > 0 ? 'inherit' : 'grey.6',
        }}
      >
        {label}
      </Text>
      <Text sx={{ color: 'grey.7', flex: '0 0 auto', fontSize: 0 }}>
        {formatPercent(percent)}% of area
      </Text>
    </Flex>
    <Progress
      variant="styles.progress.percent"
      value={percent}
      max={100}
      color={color}
      sx={{ opacity: percent > 0 ? 1 : 0.5 }}
    />
  </Box>
)

PercentBarChart.propTypes = {
  label: PropTypes.string.isRequired,
  percent: PropTypes.number,
  color: PropTypes.string,
}

PercentBarChart.defaultProps = {
  color: theme.colors.primary,
  percent: 0,
}

export default PercentBarChart
