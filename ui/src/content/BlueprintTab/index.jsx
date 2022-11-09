import React from 'react'
import PropTypes from 'prop-types'

import { Box, Heading, Text } from 'theme-ui'

import {
  useBlueprintPriorities,
  useCorridors,
  useInputAreas,
} from 'components/data'
import { OutboundLink } from 'components/link'
import NeedHelp from 'content/NeedHelp'
import { sum } from 'util/data'

import BlueprintChart from './BlueprintChart'
import CorridorsChart from './CorridorsChart'
import CorridorCategories from './CorridorCategories'
import PriorityCategories from './PriorityCategories'
import InputArea from './InputArea'

const getInputPriorities = ({
  values,
  domain,
  percents,
  label,
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
      color: '#fff7f3',
      label: `Outside ${label} input area`,
    })
  }

  if (outsideSEPercent >= 1) {
    priorities.push({
      value: -2,
      percent: outsideSEPercent,
      color: '#fde0dd',
      label: 'Outside Southeast Blueprint',
    })
  }

  return priorities
}

const BlueprintTab = ({
  blueprint,
  corridors,
  inputId,
  outsideSEPercent,
  ...mapData
}) => {
  const { all: allPriorities } = useBlueprintPriorities()
  const corridorCategories = useCorridors()
  const inputInfo = useInputAreas()[inputId]

  // Note: incoming priorities are in descending order but percents
  // are stored in ascending order
  const priorityCategories = allPriorities
    .slice()
    .reverse()
    .map(({ color, ...rest }) => ({
      ...rest,
      // add transparency to match map
      color: `${color}bf`,
    }))

  // merge inputs with priority data
  let inputPercent = 100 - outsideSEPercent
  // round percent from >99 to 100
  inputPercent = inputPercent > 99 ? 100 : inputPercent

  const {
    values: inputValues,
    domain: inputDomain,
    label: inputLabel,
  } = inputInfo

  const inputData = {
    ...inputInfo,
    percent: inputPercent,
    values: getInputPriorities({
      values: inputValues,
      domain: inputDomain,
      label: inputLabel,
      totalPercent: inputPercent,
      percents: mapData[inputId] ? mapData[inputId] : [],
      outsideSEPercent,
    }),
  }

  let hasInland = false
  let hasMarine = false
  if (corridors && corridors.length) {
    hasInland = sum(corridors.slice(0, 2)) > 0
    hasMarine = sum(corridors.slice(2, 4)) > 0
  }

  const filterCorridors = ({ value }) => {
    // always exclude not a hub / corridor
    if (value === 4) {
      return false
    }
    if (!hasInland && value <= 1) {
      return false
    }
    if (!hasMarine && value > 1) {
      return false
    }
    return true
  }

  return (
    <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
      <Box as="section">
        <Heading as="h3">Blueprint 2022 Priority</Heading>
        <Text sx={{ color: 'grey.7' }}>
          for a connected network of lands and waters
        </Text>
        <BlueprintChart
          categories={priorityCategories}
          blueprint={blueprint}
          outsideSEPercent={outsideSEPercent}
        />
        {outsideSEPercent < 100 ? (
          <PriorityCategories
            categories={priorityCategories
              .slice()
              .reverse()
              .filter(({ value }) => value > 0)}
          />
        ) : null}
      </Box>

      {inputId === 'base' ? (
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
            <Heading as="h3">Hubs and Corridors</Heading>
          </Text>

          <CorridorsChart
            categories={corridorCategories}
            corridors={corridors}
            outsideSEPercent={outsideSEPercent}
          />

          {outsideSEPercent < 100 ? (
            <CorridorCategories
              categories={corridorCategories.filter(filterCorridors)}
            />
          ) : null}
        </Box>
      ) : (
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
            <Heading as="h3">Blueprint Input</Heading>
          </Text>

          <Text sx={{ fontSize: 0, color: 'grey.7', mb: '2rem' }}>
            See{' '}
            <OutboundLink to="https://www.sciencebase.gov/catalog/file/get/62d5816fd34e87fffb2dda77?name=Southeast_Blueprint_2022_Development_Process.pdf">
              Blueprint development process
            </OutboundLink>{' '}
            for more details about how individual Blueprint inputs were
            integrated to create the final Blueprint value.{' '}
          </Text>

          <Box sx={{ mt: '1rem' }}>
            <InputArea {...inputData} />
          </Box>
        </Box>
      )}

      <NeedHelp />
    </Box>
  )
}

BlueprintTab.propTypes = {
  inputId: PropTypes.string.isRequired,
  blueprint: PropTypes.arrayOf(PropTypes.number),
  corridors: PropTypes.arrayOf(PropTypes.number),
  outsideSEPercent: PropTypes.number,
}

BlueprintTab.defaultProps = {
  blueprint: [],
  corridors: [],
  outsideSEPercent: 0,
}

export default BlueprintTab
