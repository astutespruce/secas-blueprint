import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { formatPercent } from 'util/format'

const PieChartLegend = ({ elements }) => {
  return (
    <Box sx={{ ml: '2rem', minWidth: '140px' }}>
      {elements.map(({ color, value, label }) => (
        <Flex
          key={label}
          sx={{
            align: 'center',
            mb: '0.5rem',
            fontSize: [0],
          }}
        >
          <Box
            sx={{
              width: '1.5em',
              height: '1.5em',
              mr: '0.5rem',
              flex: '0 0 auto',
              border: '1px solid #CCC',
            }}
            style={{ backgroundColor: color }}
          />
          <Flex sx={{ flexWrap: 'wrap' }}>
            <Text sx={{ mr: '0.5em' }}>{label}</Text>
            <Text sx={{ color: 'grey.7', flex: '0 0 auto' }}>
              ({formatPercent(value)}%)
            </Text>
          </Flex>
        </Flex>
      ))}
    </Box>
  )
}

PieChartLegend.propTypes = {
  elements: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      color: PropTypes.string.isRequired,
      value: PropTypes.number.isRequired,
    })
  ).isRequired,
}

export default PieChartLegend
