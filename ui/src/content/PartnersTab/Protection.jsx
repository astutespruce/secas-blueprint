import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { Check } from '@emotion-icons/fa-solid'

import { PercentBarChart } from 'components/chart'
import { useOwnership } from 'components/data'
import { OutboundLink } from 'components/link'
import { sum } from 'util/data'

const Protection = ({ type, protection }) => {
  const { protection: PROTECTION } = useOwnership()

  // handle empty protection information
  const bars = PROTECTION.map((category) => ({
    ...category,
    percent: protection ? protection[category.id] || 0 : 0,
    color: 'grey.9',
  }))

  const total = sum(bars.map(({ percent }) => Math.min(percent, 100)))

  const remainder = 100 - total
  if (remainder > 0) {
    bars.push({
      id: 'not_conserved',
      label: 'Not conserved',
      color: 'grey.5',
      percent: remainder,
    })
  }

  if (type === 'pixel') {
    return (
      <Box sx={{ ml: '0.5rem', mt: '0.5rem' }}>
        {bars.map(({ id, label, percent }) => (
          <Flex
            key={id}
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
                color: percent > 0 ? 'text' : 'grey.6',
                fontWeight: percent > 0 ? 'bold' : 'normal',
              }}
            >
              {label}
            </Text>
            {percent > 0 ? (
              <Box sx={{ flex: '0 0 auto' }}>
                <Check size="1em" />
              </Box>
            ) : null}
          </Flex>
        ))}
      </Box>
    )
  }

  return (
    <>
      {bars.map((bar) => (
        <PercentBarChart
          key={bar.id}
          {...bar}
          sx={{ mt: '0.5rem', mb: '1rem' }}
        />
      ))}

      <Text sx={{ color: 'grey.7', fontSize: 1 }}>
        {total > 100 ? (
          <>
            Note: due to overlapping protected areas compiled from multiple
            sources and designations, the sum of areas in above categories is
            more than 100% of this area.
            <br />
            <br />
          </>
        ) : null}
        Land and marine protectection status is derived from the{' '}
        <OutboundLink to="https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download">
          Protected Areas Database of the United States
        </OutboundLink>{' '}
        (PAD-US v3.0).
      </Text>
    </>
  )
}

Protection.propTypes = {
  type: PropTypes.string.isRequired,
  protection: PropTypes.objectOf(PropTypes.number),
}

Protection.defaultProps = {
  protection: {},
}

export default Protection
