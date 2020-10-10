import React from 'react'
import PropTypes from 'prop-types'

import { Box, Text, Divider, Heading } from 'theme-ui'

import SLR from './SLR'
import Urban from './Urban'

const ThreatsTab = ({ unitType, slr, urban }) => {
  if (unitType !== 'subwatershed') {
    return (
      <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
        <Text sx={{ color: 'grey.7' }}>
          No information on threats is available for marine units.
        </Text>
      </Box>
    )
  }

  return (
    <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
      <Box as="section">
        <Heading as="h3">Current and Projected Urbanization</Heading>
        {urban && urban.length > 0 ? (
          <Urban percents={urban} />
        ) : (
          <Text sx={{ color: 'grey.7' }}>
            This watershed is not impacted by projected urbanization up to 2100.
          </Text>
        )}
      </Box>

      <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

      <Box as="section">
        <Heading as="h3">Sea Level Rise</Heading>
        {slr && slr.length > 0 ? (
          <SLR percents={slr} />
        ) : (
          <Text sx={{ color: 'grey.7' }}>
            This watershed is not impacted by up to 6 feet of projected sea
            level rise.
          </Text>
        )}
      </Box>
    </Box>
  )
}

ThreatsTab.propTypes = {
  unitType: PropTypes.string.isRequired,
  slr: PropTypes.arrayOf(PropTypes.number),
  urban: PropTypes.arrayOf(PropTypes.number),
}

ThreatsTab.defaultProps = {
  slr: null,
  urban: null,
}

export default ThreatsTab
