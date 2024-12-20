import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { Check } from '@emotion-icons/fa-solid'

import { wildfireRisk as wildfireRiskCategories } from 'config'
import { OutboundLink } from 'components/link'
import { PercentBarChart } from 'components/chart'

const DataSource = () => (
  <Text sx={{ mt: '2rem', color: 'grey.8', fontSize: 1 }}>
    Wildfire likelihood data derived from the{' '}
    <OutboundLink to="https://wildfirerisk.org/">
      Wildfire Risk to Communities
    </OutboundLink>{' '}
    project by the USDA Forest Service.
  </Text>
)

const WildfireRisk = ({ type, wildfireRisk, subregions }) => {
  const bars = wildfireRiskCategories.map((category) => ({
    ...category,
    percent: wildfireRisk ? wildfireRisk[category.value] || 0 : 0,
    color: 'grey.9',
  }))

  if (type === 'pixel') {
    if (wildfireRisk === null) {
      return (
        <Box>
          <Text sx={{ color: 'grey.8' }}>
            Wildfire likelihood data is not currently available for this area.
          </Text>
        </Box>
      )
    }

    // show wildfire risk classes with checkmarks
    return (
      <Box>
        <Flex sx={{ justifyContent: 'space-between' }}>
          <Text sx={{ color: 'grey.8' }}>Wildfire likelihood:</Text>
        </Flex>
        <Box sx={{ ml: '0.5rem', mt: '0.5rem' }}>
          {wildfireRiskCategories.map(({ value, label }) => (
            <Flex
              key={value}
              sx={{
                alignItems: 'baseline',
                justifyContent: 'space-between',
                pl: '0.5rem',
                borderBottom: '1px solid',
                borderBottomColor: 'grey.2',
                pb: '0.25rem',
                '&:not(:first-of-type)': {
                  mt: '0.25rem',
                },
              }}
            >
              <Text
                sx={{
                  flex: '1 1 auto',
                  color: value === wildfireRisk ? 'text' : 'grey.8',
                  fontWeight: value === wildfireRisk ? 'bold' : 'normal',
                }}
              >
                {label}
              </Text>
              {value === wildfireRisk ? (
                <Box sx={{ flex: '0 0 auto' }}>
                  <Check size="1em" />
                </Box>
              ) : null}
            </Flex>
          ))}
        </Box>
        <DataSource />
      </Box>
    )
  }

  if ((subregions && subregions.has('Caribbean')) || wildfireRisk === null) {
    return (
      <Box>
        <Text sx={{ color: 'grey.8' }}>
          Wildfire likelihood data is not currently available for this area.
        </Text>
      </Box>
    )
  }

  return (
    <>
      <Text sx={{ color: 'grey.8' }}>
        Extent of wildfire probability by category within this subwatershed:
      </Text>
      {bars.map((bar) => (
        <PercentBarChart
          key={bar.value}
          {...bar}
          sx={{ mt: '0.5rem', mb: '1rem' }}
        />
      ))}
      <DataSource />
    </>
  )
}

WildfireRisk.propTypes = {
  type: PropTypes.string.isRequired,
  wildfireRisk: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]),
  subregions: PropTypes.object,
}

WildfireRisk.defaultProps = {
  wildfireRisk: null,
  subregions: null,
}

export default WildfireRisk
