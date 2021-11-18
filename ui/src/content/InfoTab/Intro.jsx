import React from 'react'
import { Alert, Box, Paragraph } from 'theme-ui'

import { OutboundLink } from 'components/link'

const Intro = () => (
  <>
    <Box as="section">
      <Alert sx={{ bg: 'blue.1', fontWeight: 'normal', py: '0.5em' }}>
        <Paragraph sx={{ fontSize: 1 }}>
          <b>Head&apos;s up!</b>
          <br />
          The Southeast Conservation Blueprint 2021 is now available, but not
          yet integerated into this viewer (we&apos;re working on it!). In the
          meantime, please visit the{' '}
          <OutboundLink to="https://seregion.databasin.org/galleries/38e203673ba84292a56a4a5810c26174/">
            2021 Data Gallery on the Conservation Planning Atlas
          </OutboundLink>
          <br /> for the latest version.
        </Paragraph>
      </Alert>
      <p>
        The Southeast Conservation Blueprint is the primary product of the
        Southeast Conservation Adaptation Strategy (SECAS). It is a living,
        spatial plan that identifies important areas for conservation and
        restoration across the Southeast and Caribbean. The Blueprint stitches
        together smaller subregional plans into one consistent map,
        incorporating the best available information about key species,
        ecosystems, and future threats. More than 1,700 people from 500
        different organizations have actively participated in its development so
        far.
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
        subwatersheds and marine lease blocks as well as pixel-level details of
        what indicators are driving the Blueprint conservation values.
      </p>
    </Box>
  </>
)

export default Intro
