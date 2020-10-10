import React from 'react'
import PropTypes from 'prop-types'
import { Flex } from 'theme-ui'
import { PieChart } from 'react-minimal-pie-chart'

import { PieChartLegend } from 'components/chart'
import { sum } from 'util/data'

const InputAreaPriorityChart = ({ inputLabel, values, valueLabel }) => {
  const chartWidth = 150

  const chartData = values
    ? values
        .filter(({ percent }) => percent > 0)
        .map(({ percent, ...rest }) => ({ ...rest, value: percent }))
    : []

  if (chartData.length === 0) {
    return null
  }

  const total = sum(chartData.map(({ value }) => value))

  console.log('total', total)

  if (total <= 99) {
    const remainder = 100 - total
    chartData.push({
      value: remainder,
      color: '#fdefe2',
      label: `Outside ${inputLabel} input area`,
    })
  }

  console.log('chartData', chartData)

  return (
    <Flex sx={{ alignItems: 'center', mt: '2rem' }}>
      <PieChart
        data={chartData}
        lineWidth={60}
        radius={chartWidth / 4 - 2}
        style={{
          width: chartWidth,
          flex: '0 0 auto',
        }}
      />

      <PieChartLegend title={valueLabel} elements={chartData} />
    </Flex>
  )
}

InputAreaPriorityChart.propTypes = {
  inputLabel: PropTypes.string.isRequired,
  values: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
      color: PropTypes.string.isRequired,
      percent: PropTypes.number,
    })
  ),
  valueLabel: PropTypes.string,
}

InputAreaPriorityChart.defaultProps = {
  values: null,
  valueLabel: null,
}

export default InputAreaPriorityChart
