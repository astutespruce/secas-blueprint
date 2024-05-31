import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { Check } from '@emotion-icons/fa-solid'

import { ownership as ownershipCategories } from 'config'
import { PercentBarChart } from 'components/chart'
import { sum } from 'util/data'

const Ownership = ({ type, ownership }) => {
  // handle empty ownership information
  const bars = ownershipCategories.map((category) => ({
    ...category,
    percent: ownership ? ownership[category.value] || 0 : 0,
    color: 'grey.9',
  }))

  if (type === 'pixel') {
    const total = sum(bars.map(({ percent }) => Math.min(percent, 100)))

    const remainder = 100 - total
    if (remainder > 0) {
      bars.push({
        value: 'not_conserved',
        label: 'Not conserved',
        color: 'grey.5',
        percent: remainder,
      })
    }

    return (
      <Box sx={{ ml: '0.5rem', mt: '0.5rem' }}>
        {bars.map(({ value, label, percent }) => (
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
                color: percent > 0 ? 'text' : 'grey.8',
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

  return bars.map((bar) => (
    <PercentBarChart
      key={bar.value}
      {...bar}
      sx={{ mt: '0.5rem', mb: '1rem' }}
    />
  ))
}

Ownership.propTypes = {
  type: PropTypes.string.isRequired,
  ownership: PropTypes.objectOf(PropTypes.number),
}

Ownership.defaultProps = {
  ownership: {},
}

export default Ownership
