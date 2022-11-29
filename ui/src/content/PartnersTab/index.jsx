import React from 'react'
import PropTypes from 'prop-types'

import { Box, Divider, Heading, Paragraph } from 'theme-ui'

import { OutboundLink } from 'components/link'
import NeedHelp from 'content/NeedHelp'

import Ownership from './Ownership'
import Protection from './Protection'

const PartnersTab = ({
  type,
  ownership,
  protection,
  ltaSearch,
  protectedAreas,
}) => (
  <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
    <Box as="section">
      <Heading as="h3">Conserved Areas Ownership</Heading>
      <Ownership type={type} ownership={ownership} />
    </Box>

    <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

    <Box as="section">
      <Heading as="h3">Protection Status</Heading>
      <Protection type={type} protection={protection} />
    </Box>

    {type === 'pixel' && protectedAreas && protectedAreas.length > 0 ? (
      <>
        <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

        <Box as="section">
          <Heading as="h3">Protected Areas</Heading>
          <Box as="ul" sx={{ mt: '0.5rem' }}>
            {protectedAreas.map(({ name, owner }, i) => (
              <li key={`${name}_${owner}_${i}`}>
                {name || 'Name unknown'} ({owner || 'unknown owner'})
              </li>
            ))}
          </Box>
        </Box>
      </>
    ) : null}

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
  type: PropTypes.string.isRequired,
  ownership: PropTypes.objectOf(PropTypes.number),
  protection: PropTypes.objectOf(PropTypes.number),
  ltaSearch: PropTypes.arrayOf(PropTypes.number),
  protectedAreas: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      owner: PropTypes.string,
    })
  ),
}

PartnersTab.defaultProps = {
  ownership: null,
  protection: null,
  ltaSearch: null,
  protectedAreas: null, // only present in pixel mode
}

export default PartnersTab
