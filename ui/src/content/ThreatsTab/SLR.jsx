import React from 'react'
import PropTypes from 'prop-types'

import { Box, Text } from 'theme-ui'

import { OutboundLink } from 'components/link'
import { LineChart } from 'components/chart'

// SLR levels are in feet above current mean sea level: 0...10

const SLR = ({ depth }) => {
  if (!(depth && depth.length)) {
    return (
      <Text sx={{ color: 'grey.7' }}>
        This watershed is not impacted by up to 10 feet of projected sea level
        rise or SLR data are not available for this area.
      </Text>
    )
  }

  return (
    <>
      <Text sx={{ color: 'grey.7' }}>
        Extent of flooding by projected sea level rise within this subwatershed:
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
          data={depth.map((y, i) => ({ x: i, y }))}
          fontSize={10}
          yTicks={5}
          xTicks={depth.length}
          yLabel="Percent of area"
          yLabelOffset={48}
          xLabel="Amount of sea level rise (feet)"
          xLabelOffset={40}
          areaColor="#004da8"
          areaOpacity={0.6}
          pointColor="#004da8"
          lineColor="#004da8"
          lineWidth={2}
          margin={{ left: 60, right: 10, top: 10, bottom: 50 }}
        />
      </Box>

      <Text sx={{ mt: '2rem', color: 'grey.7', fontSize: 1 }}>
        Sea level rise estimates derived from the{' '}
        <OutboundLink to="https://coast.noaa.gov/digitalcoast/data/slr.html">
          NOAA sea-level rise inundation data
        </OutboundLink>
        . To explore additional SLR information, please see NOAA&apos;s{' '}
        <OutboundLink to="https://coast.noaa.gov/slr/">
          Sea Level Rise Viewer
        </OutboundLink>
        .
      </Text>
    </>
  )
}

SLR.propTypes = {
  depth: PropTypes.arrayOf(PropTypes.number),
}

SLR.defaultProps = {
  depth: null,
}

export default SLR
