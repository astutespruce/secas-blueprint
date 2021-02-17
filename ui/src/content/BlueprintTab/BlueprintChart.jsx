import React from 'react'
import PropTypes from 'prop-types'
import { PieChart } from 'react-minimal-pie-chart'
import { Flex, Text } from 'theme-ui'

import { PieChartLegend } from 'components/chart'

const chartWidth = 150

const BlueprintChart = ({ categories, blueprint, remainder }) => {
  const blueprintChartData = blueprint
    .map((percent, i) => ({
      ...categories[i],
      value: percent,
    }))
    .filter(({ value }) => value > 0)
    .reverse()

  if (remainder) {
    blueprintChartData.push({
      value: remainder,
      color: '#EEE',
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

      {remainder < 100 ? (
        <Text sx={{ mt: '1rem', fontSize: 1, color: 'grey.7' }}>
          {blueprintChartData
            .filter(({ description }) => description)
            .map(({ label, description }, i) => (
              <React.Fragment key={label}>
                {i > 0 ? (
                  <>
                    <br />
                    <br />
                  </>
                ) : null}
                {label}: {description}
              </React.Fragment>
            ))}
        </Text>
      ) : null}
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
  remainder: PropTypes.number,
}

BlueprintChart.defaultProps = {
  blueprint: [],
  remainder: 0,
}

export default BlueprintChart