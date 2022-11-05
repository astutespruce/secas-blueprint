import React from 'react'
import PropTypes from 'prop-types'

import { Box, Text, Divider, Heading, Paragraph } from 'theme-ui'

import NeedHelp from 'content/NeedHelp'

import SLR from './SLR'
import Urban from './Urban'

const ThreatsTab = ({ unitType, slr, urban }) => {
  if (unitType !== 'subwatershed') {
    return (
      <Paragraph
        sx={{
          py: '2rem',
          px: '1rem',
          color: 'grey.7',
          textAlign: 'center',
          fontSize: 1,
        }}
      >
        No information on threats is available for marine units.
      </Paragraph>
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
        <SLR {...slr} />
      </Box>

      <NeedHelp />
    </Box>
  )
}

ThreatsTab.propTypes = {
  unitType: PropTypes.string.isRequired,
  slr: PropTypes.shape({
    depth: PropTypes.arrayOf(PropTypes.number),
    nodata: PropTypes.arrayOf(PropTypes.number),
  }),
  urban: PropTypes.arrayOf(PropTypes.number),
}

ThreatsTab.defaultProps = {
  slr: null,
  urban: null,
}

export default ThreatsTab
