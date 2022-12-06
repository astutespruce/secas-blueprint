import React from 'react'
import PropTypes from 'prop-types'

import { Box, Text } from 'theme-ui'

import { useSLR } from 'components/data'
import { OutboundLink } from 'components/link'
import { LineChart } from 'components/chart'

const DataSource = () => (
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
)

// SLR depth levels are in feet above current mean sea level: 0...10
const SLR = ({ type, depth, nodata }) => {
  const { nodata: nodataCategories } = useSLR()

  if (type === 'pixel') {
    if (nodata !== null) {
      return (
        <Box>
          <Text>{nodataCategories[nodata].label}.</Text>
          <DataSource />
        </Box>
      )
    }
    if (depth === null) {
      return (
        <Box>
          <Text sx={{ color: 'grey.7' }}>{nodataCategories[1].label}.</Text>
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

  if (nodata && nodata.length > 0) {
    for (let i = 0; i < 3; i += 1) {
      if ((type === 'pixel' && nodata === i) || nodata[i] >= 99) {
        return (
          <Box>
            <Text sx={{ color: 'grey.7' }}>{nodataCategories[i].label}.</Text>
            <DataSource />
          </Box>
        )
      }
    }
  }

  if (!(depth && depth.length > 0)) {
    return (
      <Box>
        <Text sx={{ color: 'grey.7' }}>{nodataCategories[1].label}.</Text>
        <DataSource />
      </Box>
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
