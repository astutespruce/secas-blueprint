import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { OutboundLink } from 'components/link'

const LTAList = ({ counties }) => {
  // sort by state then county
  const entries = Object.entries(counties).sort(
    ([leftState, leftCounty], [rightState, rightCounty]) => {
      if (leftState === rightState) {
        if (leftCounty < rightCounty) {
          return -1
        }
        if (leftCounty > rightCounty) {
          return 1
        }
        return 0
      }
      if (leftState < rightState) {
        return -1
      }
      return 1
    }
  )

  return (
    <Box as="ul" sx={{ mt: '0.5rem' }}>
      {entries.map(([FIPS, [state, county]]) => (
        <li key={FIPS}>
          <OutboundLink to={`http://findalandtrust.org/counties/${FIPS}`}>
            {county}, {state}
          </OutboundLink>
        </li>
      ))}
    </Box>
  )
}

LTAList.propTypes = {
  // key is FIPS, value is [state, county]
  counties: PropTypes.objectOf(PropTypes.arrayOf(PropTypes.string)).isRequired,
}

export default LTAList
