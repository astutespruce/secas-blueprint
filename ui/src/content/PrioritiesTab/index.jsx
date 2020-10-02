import React from 'react'
import PropTypes from 'prop-types'

import { PieChart } from 'react-minimal-pie-chart'
import { Box, Flex, Divider, Heading, Text } from 'theme-ui'

import { PieChartLegend } from 'components/chart'
import {
  useBlueprintCategories,
  useHubsConnectors,
  useInputAreas,
} from 'components/data'
import { OutboundLink } from 'components/link'

import { sum, sortByFunc } from 'util/data'
import { formatPercent } from 'util/format'

const PrioritiesTab = ({ blueprint, inputs, hubsConnectors }) => {
  const { all: priorityCategories } = useBlueprintCategories()
  const corridorCategories = useHubsConnectors()
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
      color: '#eceeef',
      label: 'Not a hub or connector',
    })
  }

  if (remainder >= 1) {
    hubsConnectorsChartData.push({
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
        inputBins[id] = {
          ...inputCategories[id],
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

      {binnedInputs.length > 0 ? (
        <>
          <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />
          <Box as="section">
            <Heading as="h3" sx={{ mb: '1rem' }}>
              Blueprint Inputs
            </Heading>

            {binnedInputs.map(
              ({
                id,
                label,
                version,
                percent,
                infoURL,
                dataURL,
                viewerURL,
                viewerName,
              }) => (
                <Box
                  key={id}
                  sx={{
                    '&:not(:first-of-type)': {
                      mt: '2rem',
                    },
                  }}
                >
                  <Flex sx={{ justifyContent: 'space-between', width: '100%' }}>
                    <Text sx={{ fontWeight: 'bold' }}>
                      {label} {version && version}
                    </Text>
                    <Text
                      sx={{ fontSize: 0, color: 'grey.7', textAlign: 'right' }}
                    >
                      {formatPercent(percent)}% of area
                    </Text>
                  </Flex>

                  {infoURL || dataURL || viewerURL ? (
                    <Box sx={{ ml: '1rem' }}>
                      {infoURL || dataURL ? (
                        <Flex>
                          {infoURL ? (
                            <OutboundLink to={infoURL}>
                              more information
                            </OutboundLink>
                          ) : null}

                          {infoURL && dataURL ? (
                            <Text as="span">&nbsp;&nbsp;|&nbsp;&nbsp;</Text>
                          ) : null}
                          {dataURL ? (
                            <OutboundLink to={dataURL}>
                              access data
                            </OutboundLink>
                          ) : null}
                        </Flex>
                      ) : null}

                      {viewerURL ? (
                        <Text sx={{ fontSize: 0, mt: '0.5rem' }}>
                          More detailed information for Blueprint indicators is
                          available in the{' '}
                          <OutboundLink to={viewerURL}>
                            {viewerName}
                          </OutboundLink>
                        </Text>
                      ) : null}
                    </Box>
                  ) : null}
                </Box>
              )
            )}

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

PrioritiesTab.propTypes = {
  blueprint: PropTypes.arrayOf(PropTypes.number),
  inputs: PropTypes.arrayOf(PropTypes.number),
  hubsConnectors: PropTypes.arrayOf(PropTypes.number),
}

PrioritiesTab.defaultProps = {
  blueprint: [],
  inputs: [],
  hubsConnectors: [],
}

export default PrioritiesTab
