import React from 'react'
import { Box, Flex, Text } from 'theme-ui'
import {
  ExternalLinkAlt,
  Envelope,
  ExclamationCircle,
  Comments,
} from '@emotion-icons/fa-solid'

import { OutboundLink } from 'components/link'
import {
  ContactModal,
  FeedbackModal,
  ReportProblemModal,
} from 'components/modal'
import { useBreakpoints } from './Breakpoints'

const modalLinkCSS = {
  cursor: 'pointer',
  '&:hover': {
    textDecoration: 'underline',
  },
}

const Footer = () => {
  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

  if (isMobile) return null

  return (
    <Flex
      sx={{
        alignItems: 'baseline',
        justifyContent: 'space-between',
        fontSize: 1,
        lineHeight: 1,
        px: '0.5em',
        py: '0.25em',
        bg: 'blue.9',
        color: '#FFF',
        a: {
          color: '#FFF',
        },
      }}
    >
      <Box sx={{ mr: '0.5em' }}>
        <OutboundLink to="http://secassoutheast.org/blueprint.html">
          <Flex sx={{ alignItems: 'center', px: '0.5em' }}>
            <ExternalLinkAlt size="1em" style={{ marginRight: '0.5em' }} />
            <Text>Blueprint webpage</Text>
          </Flex>
        </OutboundLink>
      </Box>

      <Box sx={{ borderLeft: '1px solid #FFF', height: '1em' }} />

      <Box>
        <ContactModal>
          <Flex sx={{ alignItems: 'center', px: '0.5em' }}>
            <Envelope size="1em" style={{ marginRight: '0.5em' }} />
            <Text sx={modalLinkCSS}>Contact Us</Text>
          </Flex>
        </ContactModal>
      </Box>

      <Box
        sx={{
          display: ['none', 'none', 'unset'],
          borderLeft: '1px solid #FFF',
          height: '1em',
        }}
      />

      <Box sx={{ display: ['none', 'none', 'unset'] }}>
        <ReportProblemModal>
          <Flex sx={{ alignItems: 'center', px: '0.5em' }}>
            <ExclamationCircle size="1em" style={{ marginRight: '0.5em' }} />
            <Text sx={modalLinkCSS}>Report a Problem</Text>
          </Flex>
        </ReportProblemModal>
      </Box>

      <Box
        sx={{
          display: ['none', 'none', 'none', 'unset'],
          borderLeft: '1px solid #FFF',
          height: '1em',
        }}
      />

      <Box sx={{ display: ['none', 'none', 'none', 'unset'] }}>
        <FeedbackModal>
          <Flex sx={{ alignItems: 'center', px: '0.5em' }}>
            <Comments size="1em" style={{ marginRight: '0.5em' }} />
            <Text sx={modalLinkCSS}>Provide Feedback</Text>
          </Flex>
        </FeedbackModal>
      </Box>

      <Box
        sx={{
          borderLeft: '1px solid #FFF',
          height: '1em',
        }}
      />

      <Text sx={{ fontSize: 0, ml: '0.5em' }}>
        Created by U.S. Fish and Wildlife Service and{' '}
        <OutboundLink to="https://astutespruce.com">Astute Spruce</OutboundLink>
      </Text>
    </Flex>
  )
}

export default Footer
