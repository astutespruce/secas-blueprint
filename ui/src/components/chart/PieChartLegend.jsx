import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { formatPercent } from 'util/format'

const PieChartLegend = ({ elements, title, subtitle, sx }) => (
  <Box sx={{ ml: '2rem', minWidth: '140px', ...sx }}>
    {title || subtitle ? (
      <Text sx={{ mb: '0.5rem' }}>
        {title ? <Text>{title}</Text> : null}

        {subtitle ? (
          <Text sx={{ fontSize: 0, color: 'grey.7' }}>{subtitle}</Text>
        ) : null}
      </Text>
    ) : null}

    {elements.map(({ color, value, label }) => (
      <Flex
        key={label}
        sx={{
          align: 'center',
          fontSize: [0],
          '&:not(:first-of-type)': {
            mt: '0.5rem',
          },
        }}
      >
        <Box
          sx={{
            width: '1.25em',
            height: '1.25em',
            mr: '0.5rem',
            flex: '0 0 auto',
            border: '1px solid #CCC',
          }}
          style={{ backgroundColor: color }}
        />
        <Flex sx={{ flexWrap: 'wrap' }}>
          <Text sx={{ mr: '0.5em' }}>{label}</Text>
          <Text sx={{ color: 'grey.6', flex: '0 0 auto' }}>
            ({formatPercent(value)}%)
          </Text>
        </Flex>
      </Flex>
    ))}
  </Box>
)

PieChartLegend.propTypes = {
  title: PropTypes.string,
  subtitle: PropTypes.string,
  elements: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      color: PropTypes.string.isRequired,
      value: PropTypes.number.isRequired,
    })
  ).isRequired,
  sx: PropTypes.object,
}

PieChartLegend.defaultProps = {
  title: null,
  subtitle: null,
  sx: {},
}

export default PieChartLegend
