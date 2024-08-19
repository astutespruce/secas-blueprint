import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { urban as urbanCategories } from 'config'
import { ResponsiveChart, UrbanChart } from 'components/chart'
import { OutboundLink } from 'components/link'

import UrbanCategories from './UrbanCategories'

const YEARS = [
  2001, 2004, 2006, 2008, 2011, 2013, 2016, 2019, 2021, 2030, 2040, 2050, 2060,
]

const DataSource = () => (
  <Text sx={{ mt: '2rem', color: 'grey.8', fontSize: 1 }}>
    Past and current (2021) urban levels based on developed land cover classes
    from the{' '}
    <OutboundLink to="https://www.usgs.gov/centers/eros/science/national-land-cover-database">
      National Land Cover Database
    </OutboundLink>
    . Future urban growth estimates derived from{' '}
    <OutboundLink to="https://www.sciencebase.gov/catalog/item/63f50297d34efa0476b04cf7">
      FUTURES model projections for the contiguous United States
    </OutboundLink>{' '}
    developed by the{' '}
    <OutboundLink to="https://cnr.ncsu.edu/geospatial/">
      Center for Geospatial Analytics
    </OutboundLink>
    , NC State University. To explore maps of additional time periods,{' '}
    <OutboundLink to="https://www.arcgis.com/apps/mapviewer/index.html?webmap=3d2eadbfd0b347eca3dcb927e9778dd9">
      click here
    </OutboundLink>
    .
  </Text>
)

const Urban = ({ type, urban, subregions }) => {
  if (type === 'pixel') {
    if (urban === null) {
      return (
        <Box>
          <Text sx={{ color: 'grey.8' }}>
            Projected future urbanization data is not currently available for
            this area.
          </Text>
        </Box>
      )
    }

    // show urban classes with checkmarks
    return (
      <Box>
        <Flex sx={{ justifyContent: 'space-between' }}>
          <Text sx={{ color: 'grey.8' }}>
            Probability of urbanization by 2060:
          </Text>
        </Flex>
        <UrbanCategories categories={urbanCategories} value={urban} />

        <DataSource />
      </Box>
    )
  }

  if (subregions && subregions.has('Caribbean')) {
    return (
      <Box>
        <Text sx={{ color: 'grey.8' }}>
          Projected future urbanization data is not currently available for this
          area.
        </Text>
      </Box>
    )
  }

  if (!(urban && urban.length)) {
    return (
      <Box>
        <Text sx={{ color: 'grey.8' }}>
          This watershed is not impacted by projected urbanization up to 2100.
        </Text>
        <DataSource />
      </Box>
    )
  }

  return (
    <>
      <Text sx={{ color: 'grey.8' }}>
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
  ]),
  subregions: PropTypes.object,
}

Urban.defaultProps = {
  urban: null,
  subregions: null,
}

export default Urban
