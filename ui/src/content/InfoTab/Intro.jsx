import React from 'react'
import { Box, Paragraph } from 'theme-ui'
import { withPrefix } from 'gatsby'

import { useBreakpoints } from 'components/layout'
import { OutboundLink } from 'components/link'

import Instructions from './Instructions'

const Intro = () => {
  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

  return (
    <>
      <Box as="section">
        <Paragraph>
          The Southeast Conservation Blueprint is the primary product of the{' '}
          <OutboundLink to="https://secassoutheast.org/">
            Southeast Conservation Adaptation Strategy
          </OutboundLink>{' '}
          (SECAS). It is a living, spatial plan to achieve the SECAS vision of a
          connected network of lands and waters across the Southeast and
          Caribbean. The Blueprint is regularly updated to incorporate new data,
          partner input, and information about on-the-ground conditions.
          <br />
          <br />
          For more information, visit the{' '}
          <OutboundLink to="https://secassoutheast.org/blueprint">
            Blueprint webpage
          </OutboundLink>
          . To view the Blueprint data and make maps, visit the{' '}
          <OutboundLink to="https://secas-fws.hub.arcgis.com/pages/blueprint">
            Blueprint page of the SECAS Atlas
          </OutboundLink>
          .
          <br />
          <br />
          The <b>Southeast Conservation Blueprint Explorer</b> is an online
          viewer designed to help you understand the Blueprint and discover how
          your area of interest scores on the Blueprint priorities, hubs and
          corridors, indicators, threats, and more. Here, you can:
        </Paragraph>
        <Box
          as="ul"
          sx={{ color: 'text', fontSize: 2, mt: '0.5rem', ml: '1rem' }}
        >
          <li>
            <b>Summarize data</b> to show charts and information for a
            subwatershed or marine lease block
          </li>
          <li>
            <b>View point data</b> to discover what is driving the Blueprint
            priorities and show values at a specific location for indicators,
            threats, and more
          </li>
          <li>
            <b>Filter the Blueprint</b> to find your part of the Blueprint by
            showing only areas that score within a certain range on indicators
            and other data
          </li>
          <li>
            <b>Upload a shapefile</b> to create detailed custom reports of the
            Blueprint, hubs and corridors, underlying indicators, and threats in
            your area
          </li>
        </Box>

        {isMobile ? (
          <Instructions />
        ) : (
          <Paragraph sx={{ mt: '1rem' }}>
            <a href={withPrefix('/help')} target="_blank" rel="noreferrer">
              Read instructions on how to use this viewer
            </a>
            .
          </Paragraph>
        )}
      </Box>
    </>
  )
}

export default Intro
