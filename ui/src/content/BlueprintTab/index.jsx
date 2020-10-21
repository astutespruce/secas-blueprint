import React from 'react'
import PropTypes from 'prop-types'

import { PieChart } from 'react-minimal-pie-chart'
import { Box, Flex, Heading, Text } from 'theme-ui'

import { PieChartLegend } from 'components/chart'
import { useBlueprintCategories, useInputAreas } from 'components/data'

import { sum, sortByFunc } from 'util/data'

import InputArea from './InputArea'

const getInputPriorities = ({
  values,
  domain,
  percents,
  inputLabel,
  totalPercent,
  outsideSEPercent,
}) => {
  // join percents to values, truncating percent at the input area

  // TODO: assign color based on number of values and which blueprint value they aggregate up to
  let priorities = values
    .map(({ value, ...rest }) => ({
      value,
      ...rest,
      percent: Math.min(percents[value] || 0, totalPercent),
    }))
    .filter(({ percent }) => percent > 0)

  console.log('raw priorities', priorities, totalPercent, outsideSEPercent)

  const notPriority = {
    value: 0,
    percent: 0,
    label: 'Not a priority',
    color: '#EEE',
  }

  // NOTE: all 0 values are treated as not a priority, strip them here and add
  // back below
  if (priorities.length > 0 && priorities[0].value === 0) {
    notPriority.percent = priorities[0].percent
    priorities = priorities.slice(1, priorities.length)
  }

  if (domain && domain[0] < domain[1]) {
    priorities = priorities.slice().reverse()
  }

  if (notPriority.percent) {
    priorities.push(notPriority)
  }

  const outsideInputPercent = 100 - outsideSEPercent - totalPercent
  if (outsideInputPercent >= 1) {
    priorities.push({
      value: -1,
      percent: outsideInputPercent,
      color: '#fdfde2',
      label: `Outside ${inputLabel} input area`,
    })
  }

  if (outsideSEPercent) {
    priorities.push({
      value: -2,
      percent: outsideSEPercent,
      color: '#fdefe2',
      label: 'Outside Southeast Blueprint',
    })
  }

  return priorities
}

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
  const outsideSEPercent = 100 - blueprintTotal

  console.log('outsideSE', outsideSEPercent)

  if (outsideSEPercent > 1) {
    blueprintChartData.push({
      value: outsideSEPercent,
      color: '#fdefe2',
      label: 'Outside Southeast Blueprint',
    })
  }

  const inputBins = {}
  let hasInputOverlaps = false

  // flatten overlapping inputs
  inputs.forEach((percent, i) => {
    if (percent === 0) {
      // we need i to map to the correct inputId, so we can't filter 0 percents
      // out in advance
      return
    }
    const inputIds = inputValues[i].split(',')
    if (inputIds.length > 1) {
      hasInputOverlaps = true
    }
    inputIds.forEach((inputId) => {
      if (inputBins[inputId] !== undefined) {
        inputBins[inputId].percent += percent
      } else {
        const { valueField } = inputCategories[inputId]
        inputBins[inputId] = {
          ...inputCategories[inputId],
          percent,
          percents:
            valueField && selectedUnit[valueField]
              ? selectedUnit[valueField]
              : [],
        }
      }
    })
  })

  // sort input areas by descending percent overlap with this area
  // and extract priority values
  const binnedInputs = Object.values(inputBins)
    .sort(sortByFunc('percent', false))
    .map(({ values, domain, label, percents, percent, ...rest }) => {
      const priorities = getInputPriorities({
        values,
        domain,
        percents,
        totalPercent: percent,
        inputLabel: label,
        outsideSEPercent,
      })
      return {
        domain,
        label,
        percent,
        ...rest,
        values: priorities,
      }
    })

  console.log('binnedInputs', binnedInputs)

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
          <Box as="section">
            <Text
              sx={{
                mt: '2rem',
                bg: 'grey.1',
                ml: '-1rem',
                mr: '-2rem',
                py: '1rem',
                pl: '1rem',
                pr: '2rem',
              }}
            >
              <Heading as="h3">Blueprint Inputs</Heading>
            </Text>

            {hasInputOverlaps ? (
              <Text sx={{ fontSize: 0, color: 'grey.7', mb: '2rem' }}>
                Note: multiple Blueprint inputs overlap in some areas.
              </Text>
            ) : null}

            <Box sx={{ mt: '1rem' }}>
              {binnedInputs.map((input) => (
                <InputArea key={input.id} {...input} />
              ))}
            </Box>
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
