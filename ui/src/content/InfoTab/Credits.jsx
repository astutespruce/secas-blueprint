import React from 'react'
import { Box, Text } from 'theme-ui'

import { OutboundLink } from 'components/link'

const Credits = () => (
  <Box as="section" sx={{ pb: '2rem' }}>
    <Text as="p" sx={{ fontSize: 1 }}>
      <b>Citation:</b> The Southeast Conservation Blueprint 2020.
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
