import React from 'react'
import { Box } from 'theme-ui'

import { OutboundLink } from 'components/link'

const Intro = () => {
  return (
    <>
      <Box as="section">
        <p>
          The Southeast Conservation Blueprint is the primary product of the
          Southeast Conservation Adaptation Strategy (SECAS). It is a living,
          spatial plan that identifies important areas for conservation and
          restoration across the Southeast and Caribbean. The Blueprint stitches
          together smaller subregional plans into one consistent map,
          incorporating the best available information about key species,
          ecosystems, and future threats. More than 1,700 people from 500
          different organizations have actively participated in its development
          so far.
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
          Blueprint conservation values and supporting information within
          subwatersheds and marine lease blocks as well as pixel-level details
          of what indicators are driving the Blueprint conservation values.
        </p>
      </Box>
    </>
  )
}

export default Intro
