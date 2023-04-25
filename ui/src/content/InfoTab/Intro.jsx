/* eslint-disable jsx-a11y/tabindex-no-positive */

import React from 'react'
import { Box, Paragraph } from 'theme-ui'

import { OutboundLink } from 'components/link'

const Intro = () => (
  <>
    <Box as="section">
      <Paragraph>
        The Southeast Conservation Blueprint is the primary product of the{' '}
        <OutboundLink to="https://secassoutheast.org/" tabIndex={1}>
          Southeast Conservation Adaptation Strategy
        </OutboundLink>{' '}
        (SECAS). It is a living, spatial plan to achieve the SECAS vision of a
        connected network of lands and waters across the Southeast and
        Caribbean. The Blueprint is regularly updated to incorporate new data,
        partner input, and information about on-the-ground conditions.
        <br />
        <br />
        For more information, visit the{' '}
        <OutboundLink to="https://secassoutheast.org/blueprint" tabIndex={1}>
          Blueprint webpage
        </OutboundLink>
        . To view the Blueprint data and make maps, visit the{' '}
        <OutboundLink
          to="https://secas-fws.hub.arcgis.com/pages/blueprint"
          tabIndex={1}
        >
          Blueprint page of the SECAS Atlas
        </OutboundLink>
        .
        <br />
        <br />
        The <b>Southeast Conservation Blueprint Explorer</b> summarizes the
        Blueprint priorities and supporting information within subwatersheds and
        marine lease blocks as well as pixel-level details of what indicators
        are driving the Blueprint priorities.
      </Paragraph>
    </Box>
  </>
)

export default Intro
