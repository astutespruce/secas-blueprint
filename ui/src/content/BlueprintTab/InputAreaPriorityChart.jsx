import React from 'react'
import PropTypes from 'prop-types'
import { Flex } from 'theme-ui'
import { PieChart } from 'react-minimal-pie-chart'

import { PieChartLegend } from 'components/chart'

/**
 * Render a pie chart of input area priority values.
 * Incoming data must already have all categories, including areas outside
 * the input or Southeast region.
 */
const InputAreaPriorityChart = ({ values, valueLabel, valueCaption }) => {
  console.log('incoming values', values, valueLabel)

  const chartWidth = 110

  const chartData = values
    ? values
        .filter(({ percent }) => percent > 0)
        .map(({ percent, ...rest }) => ({ ...rest, value: percent }))
    : []

  if (chartData.length === 0) {
    return null
  }

  return (
    <Flex sx={{ alignItems: 'center' }}>
      <PieChart
        data={chartData}
        lineWidth={60}
        radius={50}
        style={{
          width: chartWidth,
          flex: '0 1 auto',
        }}
      />

      <PieChartLegend
        title={valueLabel}
        subtitle={valueCaption}
        elements={chartData}
      />
    </Flex>
  )
}

InputAreaPriorityChart.propTypes = {
  values: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
      color: PropTypes.string.isRequired,
      percent: PropTypes.number,
    })
  ),
  valueLabel: PropTypes.string,
  valueCaption: PropTypes.string,
}

InputAreaPriorityChart.defaultProps = {
  values: null,
  valueLabel: null,
  valueCaption: null,
}

export default InputAreaPriorityChart
