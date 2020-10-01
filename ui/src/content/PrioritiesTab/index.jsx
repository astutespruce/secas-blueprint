import React from 'react'
import PropTypes from 'prop-types'

import { PieChart } from 'react-minimal-pie-chart'
import { Box, Flex, Divider, Heading, Text } from 'theme-ui'

import { PieChartLegend } from 'components/chart'
import { useBlueprintPriorities, useHubsConnectors } from 'components/data'

import { sum } from 'util/data'

const PrioritiesTab = ({ blueprint, hubsConnectors }) => {
  const { all: priorityCategories } = useBlueprintPriorities()
  const corridorCategories = useHubsConnectors()

  const chartWidth = 180

  const blueprintChartData = blueprint
    .slice()
    .reverse()
    .map((percent, i) => ({
      value: percent,
      ...priorityCategories[i],
    }))
    .filter(({ value }) => value > 0)

  const blueprintTotal = sum(blueprint)
  let remainder = 0

  if (blueprintTotal <= 99) {
    remainder = 100 - blueprintTotal
    blueprintChartData.push({
      value: remainder,
      color: '#EEE',
      label: 'Outside Southeast Blueprint',
    })
  }

  const hubsConnectorsChartData = hubsConnectors
    .map((percent, i) => {
      const { label, color } = corridorCategories[i]
      return {
        value: percent,
        label,
        color,
      }
    })
    .filter(({ value }) => value > 0)
    .reverse()

  const hubsConnectorsTotal = sum(hubsConnectors)

  if (hubsConnectorsTotal < 100 - remainder) {
    hubsConnectorsChartData.push({
      value: 100 - remainder - hubsConnectorsTotal,
      color: '#ffebc2',
      label: 'Not a hub or connector',
    })
  }

  if (remainder >= 1) {
    hubsConnectorsChartData.push({
      value: remainder,
      color: '#EEE',
      label: 'Outside Southeast Blueprint',
    })
  }

  return (
    <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
      <Box as="section">
        <Heading as="h3">Blueprint 2020 Priority</Heading>
        <Text sx={{ color: 'grey.7' }}>for shared conservation action</Text>

        <Flex sx={{ alignItems: 'center', mt: '2rem' }}>
          <PieChart
            data={blueprintChartData}
            lineWidth={60}
            radius={chartWidth / 4 - 2}
            style={{
              width: chartWidth,
              flex: '0 1 auto',
            }}
          />

          <PieChartLegend elements={blueprintChartData} />
        </Flex>
      </Box>

      {hubsConnectorsChartData.length > 0 ? (
        <>
          <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />
          <Box as="section">
            <Heading as="h3">Hubs &amp; Connectors</Heading>

            <Flex sx={{ alignItems: 'center', mt: '2rem' }}>
              <PieChart
                data={hubsConnectorsChartData}
                lineWidth={60}
                radius={chartWidth / 4 - 2}
                style={{
                  width: chartWidth,
                  flex: '0 1 auto',
                }}
              />

              <PieChartLegend elements={hubsConnectorsChartData} />
            </Flex>
          </Box>
        </>
      ) : (
        <Text sx={{ textAlign: 'center', color: 'grey.7' }}>
          No hubs or connectors in this area.
        </Text>
      )}
    </Box>
  )
}

PrioritiesTab.propTypes = {
  blueprint: PropTypes.arrayOf(PropTypes.number),
  hubsConnectors: PropTypes.arrayOf(PropTypes.number),
}

PrioritiesTab.defaultProps = {
  blueprint: [],
  hubsConnectors: [],
}

export default PrioritiesTab
