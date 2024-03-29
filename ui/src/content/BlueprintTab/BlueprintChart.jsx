import React from 'react'
import PropTypes from 'prop-types'
import { PieChart } from 'react-minimal-pie-chart'
import { Flex } from 'theme-ui'

import { PieChartLegend } from 'components/chart'

const chartWidth = 150

const BlueprintChart = ({ categories, blueprint, outsideSEPercent }) => {
  const blueprintChartData = blueprint
    .map((percent, i) => ({
      ...categories[i],
      value: percent,
    }))
    .filter(({ value }) => value > 0)
    .reverse()

  if (outsideSEPercent) {
    blueprintChartData.push({
      value: outsideSEPercent,
      color: '#fde0dd',
      label: 'Outside Southeast Blueprint',
      description: null,
    })
  }

  return (
    <>
      <Flex sx={{ alignItems: 'center', mt: '2rem' }}>
        <PieChart
          data={blueprintChartData}
          lineWidth={60}
          radius={50}
          style={{
            width: chartWidth,
            flex: '0 1 auto',
          }}
        />

        <PieChartLegend elements={blueprintChartData} />
      </Flex>
    </>
  )
}

BlueprintChart.propTypes = {
  categories: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      color: PropTypes.string.isRequired,
    })
  ).isRequired,
  blueprint: PropTypes.arrayOf(PropTypes.number),
  outsideSEPercent: PropTypes.number,
}

BlueprintChart.defaultProps = {
  blueprint: [],
  outsideSEPercent: 0,
}

export default BlueprintChart
