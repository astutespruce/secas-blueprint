import React from 'react'
import PropTypes from 'prop-types'

import { Box, Text } from 'theme-ui'

import { ResponsiveChart, UrbanChart } from 'components/chart'
import { OutboundLink } from 'components/link'

const YEARS = [
  2001, 2004, 2006, 2008, 2011, 2013, 2016, 2019, 2020, 2030, 2040, 2050, 2060,
]

const Urban = ({ percents }) => (
  <>
    <Text sx={{ color: 'grey.7' }}>
      Extent of current and projected urbanization within this subwatershed:
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
        <UrbanChart data={percents.map((y, i) => ({ x: YEARS[i], y }))} />
      </ResponsiveChart>
    </Box>

    <Text sx={{ mt: '2rem', color: 'grey.7', fontSize: 1 }}>
      Past urban levels derived from the{' '}
      <OutboundLink to="https://www.usgs.gov/centers/eros/science/national-land-cover-database">
        National Land Cover Database
      </OutboundLink>
      . Future urban growth estimates derived from the FUTURES model. Data
      provided by the{' '}
      <OutboundLink to="https://cnr.ncsu.edu/geospatial/">
        Center for Geospatial Analytics
      </OutboundLink>
      , NC State University. Current (2019) urban based on developed landcover
      from the 2019 National Landcover Database.
    </Text>
  </>
)

Urban.propTypes = {
  percents: PropTypes.arrayOf(PropTypes.number).isRequired,
}

export default Urban
