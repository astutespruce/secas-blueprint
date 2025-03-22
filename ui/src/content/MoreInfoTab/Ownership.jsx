import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { Check } from '@emotion-icons/fa-solid'

import { ownership as ownershipCategories } from 'config'
import { PercentBarChart } from 'components/chart'
import { OutboundLink } from 'components/link'

const DataSource = () => (
  <Text sx={{ mt: '3rem', color: 'grey.8', fontSize: 1 }}>
    Conserved areas are derived from the{' '}
    <OutboundLink to="https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download">
      Protected Areas Database of the United States
    </OutboundLink>{' '}
    (PAD-US v4.0 and v3.0) and include Fee, Designation, Easement, Marine, and
    Proclamation (Dept. of Defense lands only) boundaries.
  </Text>
)

const Ownership = ({ type, ownership, protectedAreas }) => {
  // handle empty ownership information
  const bars = ownershipCategories.map((category) => ({
    ...category,
    percent: ownership ? ownership[category.value] || 0 : 0,
    color: 'grey.8',
  }))

  if (type === 'pixel') {
    // show ownership with checkmarks
    return (
      <Box>
        <Box sx={{ ml: '0.5rem', mt: '0.5rem' }}>
          {ownershipCategories.map(({ value, label }) => (
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
                  color: value === ownership ? 'text' : 'grey.8',
                  fontWeight: value === ownership ? 'bold' : 'normal',
                }}
              >
                {label}
              </Text>
              {value === ownership ? (
                <Box sx={{ flex: '0 0 auto' }}>
                  <Check size="1em" />
                </Box>
              ) : null}
            </Flex>
          ))}
        </Box>

        {protectedAreas && protectedAreas.length > 0 ? (
          <Box as="section" sx={{ mt: '1rem', ml: '0.75rem' }}>
            <Text sx={{ fontWeight: 'bold' }}>
              Conserved areas at this location
            </Text>
            <Box as="ul" sx={{ mt: '0.5rem', ml: '1rem' }}>
              {protectedAreas.map(({ name, owner }, i) => (
                /* eslint-disable-next-line react/no-array-index-key */
                <li key={`${name}_${owner}_${i}`}>
                  {name || 'Name unknown'} {owner ? ` (${owner})` : null}
                </li>
              ))}
            </Box>
          </Box>
        ) : null}

        <DataSource />
      </Box>
    )
  }

  return (
    <>
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

Ownership.propTypes = {
  type: PropTypes.string.isRequired,
  ownership: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]),
  protectedAreas: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      owner: PropTypes.string,
    })
  ),
}

Ownership.defaultProps = {
  ownership: [],
  protectedAreas: null,
}

export default Ownership
