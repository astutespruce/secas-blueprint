import React from 'react'
import { Box } from 'theme-ui'

import { OutboundLink } from 'components/link'

const Intro = () => (
  <>
    <Box as="section">
      <p>
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
        The <b>Southeast Conservation Blueprint Explorer</b> summarizes the
        Blueprint priorities and supporting information within subwatersheds and
        marine lease blocks. Pixel-level functionality coming soon!
        {/* TODO: */}
        {/* as well as pixel-level details of what indicators
        are driving the Blueprint priorities. */}
      </p>
    </Box>
  </>
)

export default Intro
