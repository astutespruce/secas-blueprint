import React from 'react'
import PropTypes from 'prop-types'

import { Box, Text } from 'theme-ui'

import { slrNodata } from 'config'
import { OutboundLink } from 'components/link'
import { LineChart } from 'components/chart'
import { formatPercent } from 'util/format'

const DataSource = () => (
  <Text sx={{ mt: '2rem', color: 'grey.8', fontSize: 1 }}>
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
)

// SLR depth levels are in feet above current mean sea level: 0...10
const SLR = ({ type, depth, nodata }) => {
  if (type === 'pixel') {
    if (nodata !== null) {
      return (
        <Box>
          <Text>{slrNodata[nodata].label}.</Text>
          <DataSource />
        </Box>
      )
    }
    if (depth === null) {
      return (
        <Box>
          <Text sx={{ color: 'grey.8' }}>{slrNodata[2].label}.</Text>
          <DataSource />
        </Box>
      )
    }

    if (depth === 0) {
      return (
        <Box>
          <Text>This area is already inundated.</Text>
          <DataSource />
        </Box>
      )
    }

    return (
      <Box>
        <Text>
          This area is projected to be inundated at{' '}
          <b>
            {depth} {depth === 1 ? 'foot' : 'feet'}
          </b>{' '}
          of sea-level rise.
        </Text>
        <DataSource />
      </Box>
    )
  }

  const nodataItems = []
  if (nodata && nodata.length > 0) {
    for (let i = 0; i < 3; i += 1) {
      // if pixel mode or mostly a single type of nodata, return just that
      if ((type === 'pixel' && nodata === i) || nodata[i] >= 99) {
        return (
          <Box>
            <Text sx={{ color: 'grey.8' }}>{slrNodata[i].label}.</Text>
            <DataSource />
          </Box>
        )
      }
      if (nodata[i] > 1) {
        nodataItems.push(
          `${slrNodata[i].label
            .toLowerCase()
            .replace(/this area is/g, '')
            .replace(/for this area/g, '')
            .trim()} (${formatPercent(nodata[i])}% of area)`
        )
      }
    }
  }

  if (!(depth && depth.length > 0)) {
    return (
      <Box>
        <Text sx={{ color: 'grey.8' }}>{slrNodata[2].label}.</Text>
        <DataSource />
      </Box>
    )
  }

  return (
    <>
      <Text sx={{ color: 'grey.8' }}>
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
      {nodataItems.length > 0 ? (
        <Text sx={{ mt: '2rem', color: 'grey.8', fontSize: 1 }}>
          This subwatershed has additional areas not included in the chart
          above: {nodataItems.join(', ')}.
        </Text>
      ) : null}
      <DataSource />
    </>
  )
}

SLR.propTypes = {
  type: PropTypes.string.isRequired,
  depth: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]),
  nodata: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]),
}

SLR.defaultProps = {
  depth: null,
  nodata: null,
}

export default SLR
