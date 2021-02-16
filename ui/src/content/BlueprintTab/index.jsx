import React from 'react'
import PropTypes from 'prop-types'

import { Box, Heading, Text } from 'theme-ui'

import { useBlueprintPriorities, useInputAreas } from 'components/data'
import { OutboundLink } from 'components/link'
import { sum, sortByFunc } from 'util/data'

import BlueprintChart from './BlueprintChart'
import InputArea from './InputArea'

const getInputPriorities = ({
  values,
  domain,
  percents,
  inputLabel,
  totalPercent,
  outsideSEPercent,
}) => {
  if (!values) {
    return []
  }
  // join percents to values, truncating percent at the input area
  let priorities = values
    .map(({ value, ...rest }) => ({
      value,
      ...rest,
      percent: Math.min(percents[value] || 0, totalPercent),
    }))
    .filter(({ percent }) => percent > 0)

  // if any are >99%, keep only the first and round up to 100%
  const over99 = priorities.filter(({ percent }) => percent > 99)
  if (over99.length > 0) {
    priorities = [over99[0]]
    priorities[0].percent = 100
  }

  const notPriority = {
    value: 0,
    percent: 0,
    label: 'Not a priority',
    color: '#ffebc2',
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
      color: '#BBB',
      label: `Outside ${inputLabel} input area`,
    })
  }

  if (outsideSEPercent >= 1) {
    priorities.push({
      value: -2,
      percent: outsideSEPercent,
      color: '#EEE',
      label: 'Outside Southeast Blueprint',
    })
  }

  return priorities
}

const BlueprintTab = ({ blueprint, inputs, ...mapData }) => {
  const { all: allPriorities } = useBlueprintPriorities()
  const { inputs: inputCategories, values: inputValues } = useInputAreas()

  // Note: incoming priorities are in descending order but percents
  // are stored in ascending order
  const priorityCategories = allPriorities.slice().reverse()

  let remainder = 0
  remainder = 100 - sum(blueprint)
  if (remainder < 1) {
    remainder = 0
  }

  const outsideSEPercent = 100 - sum(blueprint)

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
            valueField && mapData[valueField] ? mapData[valueField] : [],
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

        // round percent from >99 to 100
        percent: percent > 99 ? 100 : percent,
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
        <BlueprintChart
          categories={priorityCategories}
          blueprint={blueprint}
          remainder={remainder}
        />
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

            <Text sx={{ fontSize: 0, color: 'grey.7', mb: '2rem' }}>
              See{' '}
              <OutboundLink to="https://www.sciencebase.gov/catalog/file/get/5f85ac8282cebef40f14c545?name=SE_Blueprint_2020_DevelopmentProcess.pdf">
                Blueprint integration documentation
              </OutboundLink>{' '}
              for more details about how individual Blueprint inputs were
              integrated to create the final Blueprint value.{' '}
              {hasInputOverlaps ? (
                <>
                  Note: multiple Blueprint inputs overlap in some areas; this
                  may affect the final Blueprint conservation value.
                </>
              ) : null}
            </Text>

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
