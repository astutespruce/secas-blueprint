import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Divider, Heading, Paragraph, Text } from 'theme-ui'

import { OutboundLink } from 'components/link'
import NeedHelp from 'content/NeedHelp'

import Ownership from './Ownership'
import Protection from './Protection'
import SLR from './SLR'
import Urban from './Urban'

const MoreInfoTab = ({
  type,
  slr,
  urban,
  subregions,
  ownership,
  protection,
  ltaSearch,
  protectedAreas,
}) => {
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
        <Urban type={type} urban={urban} subregions={subregions} />
      </Box>

      <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

      <Box as="section">
        <Flex sx={{ justifyContent: 'space-between', alignItems: 'baseline' }}>
          <Heading as="h3">Sea Level Rise</Heading>
        </Flex>
        <SLR type={type} {...slr} />
      </Box>

      <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

      <Box as="section">
        <Heading as="h3">Conserved Areas Ownership</Heading>
        <Ownership type={type} ownership={ownership} />
      </Box>

      <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

      <Box as="section" sx={{ mt: '3rem' }}>
        <Heading as="h3">Protection Status</Heading>
        <Protection type={type} protection={protection} />
      </Box>

      {type === 'pixel' && protectedAreas && protectedAreas.length > 0 ? (
        <Box as="section" sx={{ mt: '3rem' }}>
          <Heading as="h3">Protected Areas</Heading>
          <Box as="ul" sx={{ mt: '0.5rem' }}>
            {protectedAreas.map(({ name, owner }, i) => (
              /* eslint-disable-next-line react/no-array-index-key */
              <li key={`${name}_${owner}_${i}`}>
                {name || 'Name unknown'} ({owner || 'unknown owner'})
              </li>
            ))}
          </Box>
        </Box>
      ) : null}

      <Text sx={{ mt: '3rem', color: 'grey.8', fontSize: 1 }}>
        Land and marine ownership and protection status is derived from the{' '}
        <OutboundLink to="https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download">
          Protected Areas Database of the United States
        </OutboundLink>{' '}
        (PAD-US v4.0 and v3.0) and include Fee, Designation, Easement, Marine,
        and Proclamation (Dept. of Defense lands only) boundaries. Note: PAD-US
        includes protected areas that may overlap within a given area; this may
        cause the area within and between protection categories to be greater
        than the actual ground area.
      </Text>

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
}

MoreInfoTab.propTypes = {
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
  subregions: PropTypes.object,
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

MoreInfoTab.defaultProps = {
  slr: null,
  urban: null,
  subregions: null,
  ownership: null,
  protection: null,
  ltaSearch: null,
  protectedAreas: null, // only present in pixel mode
}

export default MoreInfoTab
