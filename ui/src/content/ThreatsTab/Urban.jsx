import React from 'react'
import PropTypes from 'prop-types'

import { Box, Text } from 'theme-ui'

import { LineChart } from 'components/chart'
import { OutboundLink } from 'components/link'

// Actual urban in 2009, then projected from 2020 onward
// shifted to 2010 for even scale
const LEVELS = [2010, 2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]

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
      }}
    >
      <LineChart
        data={percents.map((y, i) => ({ x: LEVELS[i], y }))}
        fontSize={10}
        yTicks={5}
        xTicks={6}
        xTickFormatter={(x) => x}
        yLabel="Percent of area"
        yLabelOffset={48}
        xLabel="Decade"
        xLabelOffset={40}
        areaColor="#D90000"
        areaOpacity={0.6}
        pointColor="#D90000"
        lineColor="#D90000"
        lineWidth={2}
        margin={{ left: 60, right: 10, top: 10, bottom: 50 }}
      />
    </Box>

    <Text sx={{ mt: '2rem', color: 'grey.7', fontSize: 1 }}>
      Urban growth estimates derived from the FUTURES model. Data provided by
      the{' '}
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
