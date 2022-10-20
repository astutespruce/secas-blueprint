import React from 'react'
import { Box, Text } from 'theme-ui'

import { OutboundLink } from 'components/link'

const Credits = () => (
  <Box as="section">
    <Text as="p" sx={{ fontSize: 1 }}>
      <b>Citation:</b> Southeast Conservation Adaptation Strategy (SECAS). 2022.
      Southeast Conservation Blueprint 2022.{' '}
      <OutboundLink to="http://secassoutheast.org/blueprint">
        http://secassoutheast.org/blueprint
      </OutboundLink>
      .
      <br />
      <br />
      This application was developed by{' '}
      <OutboundLink to="https://astutespruce.com">
        Astute Spruce, LLC
      </OutboundLink>{' '}
      in partnership with the U.S. Fish and Wildlife Service under the{' '}
      <OutboundLink to="http://secassoutheast.org/">
        Southeast Conservation Adaptation Strategy
      </OutboundLink>
      .
    </Text>
  </Box>
)

export default Credits
