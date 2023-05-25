import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Divider, Heading, Paragraph } from 'theme-ui'

import NeedHelp from 'content/NeedHelp'

import SLR from './SLR'
import Urban from './Urban'

const ThreatsTab = ({ type, slr, urban }) => {
  if (type !== 'pixel' && type !== 'subwatershed') {
    return (
      <Paragraph
        sx={{
          py: '2rem',
          px: '1rem',
          color: 'grey.8',
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
        <Flex sx={{ justifyContent: 'space-between', alignItems: 'baseline' }}>
          <Heading as="h3">Urbanization</Heading>
        </Flex>
        <Urban type={type} urban={urban} />
      </Box>

      <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

      <Box as="section">
        <Flex sx={{ justifyContent: 'space-between', alignItems: 'baseline' }}>
          <Heading as="h3">Sea Level Rise</Heading>
        </Flex>
        <SLR type={type} {...slr} />
      </Box>

      <NeedHelp />
    </Box>
  )
}

ThreatsTab.propTypes = {
  type: PropTypes.string.isRequired,
  slr: PropTypes.shape({
    depth: PropTypes.oneOfType([
      PropTypes.arrayOf(PropTypes.number),
      PropTypes.number,
    ]),
    nodata: PropTypes.oneOfType([
      PropTypes.arrayOf(PropTypes.number),
      PropTypes.number,
    ]),
  }),
  urban: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]),
}

ThreatsTab.defaultProps = {
  slr: null,
  urban: null,
}

export default ThreatsTab
