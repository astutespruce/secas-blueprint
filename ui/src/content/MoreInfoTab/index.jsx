import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Divider, Heading } from 'theme-ui'

import NeedHelp from 'content/NeedHelp'

import ProtectedAreas from './ProtectedAreas'
import SLR from './SLR'
import Urban from './Urban'
import WildfireRisk from './WildfireRisk'

const MoreInfoTab = ({
  type,
  slr,
  urban,
  wildfireRisk,
  subregions,
  protectedAreas,
  protectedAreasList,
  numProtectedAreas,
}) => (
  <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
    {type === 'pixel' || type === 'subwatershed' ? (
      <>
        <Box as="section">
          <Flex
            sx={{ justifyContent: 'space-between', alignItems: 'baseline' }}
          >
            <Heading as="h3">Urbanization</Heading>
          </Flex>
          <Urban type={type} urban={urban} subregions={subregions} />
        </Box>

        <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

        <Box as="section">
          <Flex
            sx={{ justifyContent: 'space-between', alignItems: 'baseline' }}
          >
            <Heading as="h3">Sea Level Rise</Heading>
          </Flex>
          <SLR type={type} {...slr} />
        </Box>

        <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />

        <Box as="section">
          <Flex
            sx={{ justifyContent: 'space-between', alignItems: 'baseline' }}
          >
            <Heading as="h3">Wildfire Likelihood</Heading>
          </Flex>
          <WildfireRisk
            type={type}
            wildfireRisk={wildfireRisk}
            subregions={subregions}
          />
        </Box>

        <Divider variant="styles.hr.light" sx={{ my: '3rem' }} />
      </>
    ) : null}

    <Box as="section">
      <Heading as="h3">Protected Areas</Heading>
      <ProtectedAreas
        type={type}
        protectedAreas={protectedAreas}
        protectedAreasList={protectedAreasList}
        numProtectedAreas={numProtectedAreas}
      />
    </Box>

    <NeedHelp />
  </Box>
)

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
  wildfireRisk: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]),
  subregions: PropTypes.object,
  protectedAreas: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]),
  protectedAreasList: PropTypes.arrayOf(PropTypes.string),
  numProtectedAreas: PropTypes.number,
}

MoreInfoTab.defaultProps = {
  slr: null,
  urban: null,
  wildfireRisk: null,
  subregions: null,
  protectedAreas: null,
  protectedAreasList: null,
  numProtectedAreas: 0,
}

export default MoreInfoTab
