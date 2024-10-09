import React from 'react'
import { Box, Flex, Divider, Paragraph, Image } from 'theme-ui'

import { OutboundLink } from 'components/link'
import SECASLogo from 'images/SECAS_logo.svg'

const Credits = () => (
  <>
    <Divider />
    <Box as="section">
      <Flex sx={{ flexWrap: 'wrap', gap: '1rem' }}>
        <Box sx={{ flex: '0 0 auto' }}>
          <Image src={SECASLogo} sx={{ width: '64px' }} alt="SECAS logo" />
        </Box>
        <Box sx={{ flex: '1 1 auto', width: ['100%', '264px'] }}>
          <Paragraph sx={{ fontSize: 1 }}>
            <b>Citation:</b> Southeast Conservation Adaptation Strategy (SECAS).
            2024. Southeast Conservation Blueprint 2024.{' '}
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
  </>
)

export default Credits
