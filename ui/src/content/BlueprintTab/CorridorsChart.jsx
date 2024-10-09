import React from 'react'
import PropTypes from 'prop-types'
import { PieChart } from 'react-minimal-pie-chart'
import { Box, Flex, Paragraph } from 'theme-ui'

import { PieChartLegend } from 'components/chart'

const chartWidth = 140

const CorridorsChart = ({ categories, corridors, outsideSEPercent }) => {
  const corridorChartData = corridors
    .map((percent, i) => {
      const { label, color } = categories[i]
      return {
        value: percent,
        label,
        color,
      }
    })
    .filter(({ value }) => value > 0)

  if (outsideSEPercent >= 1) {
    corridorChartData.push({
      value: outsideSEPercent,
      color: '#fde0dd',
      label: 'Outside Southeast Blueprint',
    })
  }

  return (
    <Box>
      <Paragraph sx={{ color: 'grey.8', fontSize: 1 }}>
        The Blueprint uses a least-cost path connectivity analysis to identify
        corridors that link hubs.
      </Paragraph>
      <Flex sx={{ alignItems: 'center', mt: '2rem' }}>
        <PieChart
          data={corridorChartData}
          lineWidth={60}
          radius={chartWidth / 3 - 2}
          style={{
            width: chartWidth,
            flex: '0 1 auto',
          }}
        />

        <PieChartLegend elements={corridorChartData} />
      </Flex>
    </Box>
  )
}

CorridorsChart.propTypes = {
  categories: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      color: PropTypes.string,
    })
  ).isRequired,
  corridors: PropTypes.arrayOf(PropTypes.number),
  outsideSEPercent: PropTypes.number,
}

CorridorsChart.defaultProps = {
  corridors: [],
  outsideSEPercent: 0,
}

export default CorridorsChart
