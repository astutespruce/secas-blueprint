import React from 'react'
import { Box, Flex, Paragraph, Image } from 'theme-ui'

import { OutboundLink } from 'components/link'
import SECASLogo from 'images/SECAS-logo-bw.svg'

const Credits = () => (
  <Box as="section">
    <Flex>
      <Box sx={{ flex: '0 0 auto' }}>
        <Image src={SECASLogo} sx={{ width: '120px' }} />
      </Box>
      <Box sx={{ flex: '1 1 auto' }}>
        <Paragraph sx={{ fontSize: 1, pl: '1rem' }}>
          <b>Citation:</b> Southeast Conservation Adaptation Strategy (SECAS).
          2022. Southeast Conservation Blueprint 2022.{' '}
          <OutboundLink to="http://secassoutheast.org/blueprint">
            http://secassoutheast.org/blueprint
          </OutboundLink>
          .
        </Paragraph>
      </Box>
    </Flex>
    <Paragraph sx={{ fontSize: 1, pt: '1rem' }}>
      This application was developed by{' '}
      <OutboundLink to="https://astutespruce.com">
        Astute Spruce, LLC
      </OutboundLink>{' '}
      in partnership with the U.S. Fish and Wildlife Service under the{' '}
      <OutboundLink to="http://secassoutheast.org/">
        Southeast Conservation Adaptation Strategy
      </OutboundLink>
      .
    </Paragraph>
  </Box>
)

export default Credits
