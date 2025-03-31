import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { Check } from '@emotion-icons/fa-solid'

import { protectedAreas as categories } from 'config'
import { PercentBarChart } from 'components/chart'
import { OutboundLink } from 'components/link'

const DataSource = ({ addOverlapNote = false }) => (
  <Text sx={{ mt: '2rem', color: 'grey.8', fontSize: 1 }}>
    Protected areas are derived from the{' '}
    <OutboundLink to="https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download">
      Protected Areas Database of the United States
    </OutboundLink>{' '}
    (PAD-US v4.0 and v3.0) and include Fee, Designation, Easement, Marine, and
    Proclamation (Dept. of Defense lands only) boundaries.{' '}
    {addOverlapNote ? (
      <>
        Areas are listed based on name, ownership, and boundary information in
        the Protected Areas Database of the United States, which may include
        overlapping and duplicate areas.
      </>
    ) : null}
  </Text>
)

DataSource.propTypes = {
  addOverlapNote: PropTypes.bool,
}

DataSource.defaultProps = {
  addOverlapNote: false,
}

const ProtectedAreas = ({
  type,
  protectedAreas,
  protectedAreasList,
  numProtectedAreas,
}) => {
  // handle empty protected areas information
  const bars = categories.map((category) => ({
    ...category,
    percent: protectedAreas ? protectedAreas[category.value] || 0 : 0,
    color: 'grey.8',
  }))

  const listOfProtectedAreas = (
    <>
      {protectedAreasList && protectedAreasList.length > 0 ? (
        <Box as="section" sx={{ mt: '1.5rem' }}>
          <Text sx={{ fontWeight: 'bold' }}>
            Protected areas at this location
          </Text>
          <Box as="ul" sx={{ mt: '0.5rem' }}>
            {protectedAreasList.map((name, i) => (
              /* eslint-disable-next-line react/no-array-index-key */
              <li key={`${name}_${i}`}>{name}</li>
            ))}
            {numProtectedAreas &&
            numProtectedAreas - protectedAreasList.length > 0 ? (
              <li>
                ...and {numProtectedAreas - protectedAreasList.length} more...
              </li>
            ) : null}
          </Box>
        </Box>
      ) : null}
    </>
  )

  if (type === 'pixel') {
    // show categories with checkmarks
    return (
      <Box>
        <Box sx={{ ml: '0.5rem', mt: '0.5rem' }}>
          {categories.map(({ value, label }) => (
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
                  color: value === protectedAreas ? 'text' : 'grey.8',
                  fontWeight: value === protectedAreas ? 'bold' : 'normal',
                }}
              >
                {label}
              </Text>
              {value === protectedAreas ? (
                <Box sx={{ flex: '0 0 auto' }}>
                  <Check size="1em" />
                </Box>
              ) : null}
            </Flex>
          ))}
        </Box>

        {listOfProtectedAreas}

        <DataSource
          addOverlapNote={protectedAreasList && protectedAreasList.length > 0}
        />
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

      {listOfProtectedAreas}

      <DataSource
        addOverlapNote={protectedAreasList && protectedAreasList.length > 0}
      />
    </>
  )
}

ProtectedAreas.propTypes = {
  type: PropTypes.string.isRequired,
  protectedAreas: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]),
  protectedAreasList: PropTypes.arrayOf(PropTypes.string),
  numProtectedAreas: PropTypes.number,
}

ProtectedAreas.defaultProps = {
  protectedAreas: [],
  protectedAreasList: [],
  numProtectedAreas: 0,
}

export default ProtectedAreas
