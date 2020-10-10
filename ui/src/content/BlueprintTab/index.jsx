import React from 'react'
import PropTypes from 'prop-types'

import { PieChart } from 'react-minimal-pie-chart'
import { Box, Flex, Divider, Heading, Text } from 'theme-ui'

import { PieChartLegend } from 'components/chart'
import { useBlueprintCategories, useInputAreas } from 'components/data'

import { sum, sortByFunc } from 'util/data'

import InputArea from './InputArea'

const BlueprintTab = ({ blueprint, inputs, ...selectedUnit }) => {
  const { all: priorityCategories } = useBlueprintCategories()
  const { inputs: inputCategories, values: inputValues } = useInputAreas()

  const chartWidth = 150

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
      color: '#fdefe2',
      label: 'Outside Southeast Blueprint',
    })
  }

  const inputBins = {}
  let hasInputOverlaps = false

  inputs.forEach((percent, i) => {
    if (percent === 0) {
      return
    }
    const ids = inputValues[i].split(',')
    if (ids.length > 1) {
      hasInputOverlaps = true
    }

    ids.forEach((id) => {
      if (inputBins[id] !== undefined) {
        inputBins[id].percent += percent
      } else {
        const category = inputCategories[id]
        const { valueField, values } = category
        inputBins[id] = {
          ...category,
          values:
            valueField && selectedUnit[valueField]
              ? values.map(({ value, ...rest }) => {
                  const percents = selectedUnit[valueField]
                  return {
                    value,
                    ...rest,
                    percent: percents[value] || 0,
                  }
                })
              : [],
          percent,
        }
      }
    })
  })

  const binnedInputs = Object.values(inputBins).sort(
    sortByFunc('percent', false)
  )

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
              flex: '0 0 auto',
            }}
          />

          <PieChartLegend elements={blueprintChartData} />
        </Flex>
      </Box>

      {binnedInputs.length > 0 ? (
        <>
          <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />
          <Box as="section">
            <Heading as="h3" sx={{ mb: '1rem' }}>
              Blueprint Inputs
            </Heading>

            {binnedInputs.map((input) => (
              <InputArea key={input.id} {...input} />
            ))}

            {hasInputOverlaps ? (
              <Text sx={{ fontSize: 0, color: 'grey.7', mt: '1rem' }}>
                Note: multiple Blueprint inputs overlap in some areas.
              </Text>
            ) : null}
          </Box>
        </>
      ) : null}
    </Box>
  )
}

BlueprintTab.propTypes = {
  blueprint: PropTypes.arrayOf(PropTypes.number),
  inputs: PropTypes.arrayOf(PropTypes.number),
}

BlueprintTab.defaultProps = {
  blueprint: [],
  inputs: [],
}

export default BlueprintTab
