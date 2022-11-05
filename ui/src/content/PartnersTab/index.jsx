import React from 'react'
import PropTypes from 'prop-types'

import { Box, Divider, Heading, Paragraph } from 'theme-ui'

import { OutboundLink } from 'components/link'
import NeedHelp from 'content/NeedHelp'

import Ownership from './Ownership'
import Protection from './Protection'

const PartnersTab = ({ ownership, protection, ltaSearch }) => (
  <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
    <Box as="section">
      <Heading as="h3">Conserved Areas Ownership</Heading>
      <Ownership ownership={ownership} />
    </Box>

    <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

    <Box as="section">
      <Heading as="h3">Protection Status</Heading>
      <Protection protection={protection} />
    </Box>

    {ltaSearch && ltaSearch.length ? (
      <>
        <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

        <Box as="section">
          <Heading as="h3">Nearby land trusts</Heading>
          <Paragraph sx={{ fontSize: 1 }}>
            {/* NOTE: the search parameters are in y,x order */}
            <OutboundLink
              to={`https://landtrustalliance.org/land-trusts/explore?nearby=false&location=${
                ltaSearch[1]
              }%2C${ltaSearch[0]}&radius=${ltaSearch[2] * 1609.34}`}
            >
              Click here
            </OutboundLink>{' '}
            to search for land trusts within {ltaSearch[2]} miles of this area
            on the Land Trust Alliance website.
          </Paragraph>
        </Box>
      </>
    ) : null}

    <NeedHelp />
  </Box>
)

PartnersTab.propTypes = {
  ownership: PropTypes.objectOf(PropTypes.number),
  protection: PropTypes.objectOf(PropTypes.number),
  ltaSearch: PropTypes.arrayOf(PropTypes.number),
}

PartnersTab.defaultProps = {
  ownership: null,
  protection: null,
  ltaSearch: null,
}

export default PartnersTab
