import React from 'react'
import PropTypes from 'prop-types'

import { Box, Text } from 'theme-ui'

import { useUrban } from 'components/data'
import { ResponsiveChart, UrbanChart } from 'components/chart'
import { OutboundLink } from 'components/link'

import UrbanCategories from './UrbanCategories'

const YEARS = [
  2001, 2004, 2006, 2008, 2011, 2013, 2016, 2019, 2020, 2030, 2040, 2050, 2060,
]

const DataSource = () => (
  <Text sx={{ mt: '2rem', color: 'grey.7', fontSize: 1 }}>
    Past and current (2019) urban levels based on developed land cover classes
    from the{' '}
    <OutboundLink to="https://www.usgs.gov/centers/eros/science/national-land-cover-database">
      National Land Cover Database
    </OutboundLink>
    . Future urban growth estimates derived from the FUTURES model. Data
    provided by the{' '}
    <OutboundLink to="https://cnr.ncsu.edu/geospatial/">
      Center for Geospatial Analytics
    </OutboundLink>
    , NC State University.
  </Text>
)

const Urban = ({ type, urban }) => {
  const urbanCategories = useUrban()

  if (type === 'pixel') {
    // show urban classes with checkmarks
    return (
      <Box>
        <Text sx={{ color: 'grey.7' }}>
          Probability of urbanization by 2060:
        </Text>
        <UrbanCategories categories={urbanCategories} value={urban} />
        <DataSource />
      </Box>
    )
  }

  if (!(urban && urban.length)) {
    return (
      <Box>
        <Text sx={{ color: 'grey.7' }}>
          This watershed is not impacted by projected urbanization up to 2100.
        </Text>
        <DataSource />
      </Box>
    )
  }

  return (
    <>
      <Text sx={{ color: 'grey.7' }}>
        Extent of past, current, and projected urbanization within this
        subwatershed:
      </Text>

      <Box
        sx={{
          height: '200px',
          '& text': {
            fontSize: 1,
            fill: 'grey.7',
          },
          '& text.label': {
            fontSize: 0,
            fill: 'grey.7',
          },
        }}
      >
        <ResponsiveChart>
          <UrbanChart data={urban.map((y, i) => ({ x: YEARS[i], y }))} />
        </ResponsiveChart>
      </Box>
      <DataSource />
    </>
  )
}

Urban.propTypes = {
  type: PropTypes.string.isRequired,
  urban: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]).isRequired,
}

export default Urban
