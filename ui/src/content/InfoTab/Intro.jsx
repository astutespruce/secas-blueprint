import React from 'react'
import { Box } from 'theme-ui'

import { OutboundLink } from 'components/link'

const Intro = () => {
  return (
    <>
      <Box as="section">
        <p>
          The Blueprint is a living, spatial plan that identifies important
          places for conservation and restoration across the Southeast and
          Caribbean. It is helping more than 200 people from over 90
          organizations bring in new funding and inform their conservation
          decisions.
          <br />
          <br />
          ...content from SECAS here...
          <br />
          <br />
          For more information, visit{' '}
          <OutboundLink to="http://secassoutheast.org/blueprint.html">
            the Blueprint webpage
          </OutboundLink>
          .
          <br />
          <br />
          If you want to overlay additional datasets or download Blueprint data,
          visit{' '}
          <OutboundLink to="https://seregion.databasin.org/">
            the Conservation Planning Atlas
          </OutboundLink>{' '}
          (CPA).
        </p>

        <p>
          The <b>Southeast Conservation Blueprint Explorer</b> summarizes the
          Blueprint priorities and supporting information within subwatersheds
          and marine lease blocks as well as pixel-level details of what
          indicators are driving the Blueprint priorities.
        </p>
      </Box>
    </>
  )
}

export default Intro
