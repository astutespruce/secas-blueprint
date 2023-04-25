/* eslint-disable jsx-a11y/tabindex-no-positive */

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
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: [0, 0, 0, 1],
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
      <Flex
        sx={{
          alignItems: 'center',
          px: '0.5em',
          mr: '0.5rem',
        }}
      >
        Version: Southeast Blueprint 2022
      </Flex>

      <Box
        sx={{
          borderLeft: '1px solid #FFF',
          height: '1em',
        }}
      />

      <Box sx={{ mx: '0.5em', flex: '0 0 auto' }}>
        <OutboundLink to="http://secassoutheast.org/blueprint" tabIndex={1}>
          <Flex sx={{ alignItems: 'center', px: '0.5em' }}>
            <ExternalLinkAlt size="1em" style={{ marginRight: '0.5em' }} />
            <Text>Blueprint webpage</Text>
          </Flex>
        </OutboundLink>
      </Box>

      <Box
        sx={{ flex: '0 0 auto', borderLeft: '1px solid #FFF', height: '1em' }}
      />

      <Box sx={{ mx: '0.5em', flex: '0 0 auto' }}>
        <ContactModal tabIndex="0">
          <Flex sx={{ alignItems: 'center', px: '0.5em' }}>
            <Envelope size="1em" style={{ marginRight: '0.5em' }} />
            <Text sx={modalLinkCSS}>Contact Us</Text>
          </Flex>
        </ContactModal>
      </Box>

      <Box
        sx={{
          display: ['none', 'none', 'unset'],
          flex: '0 0 auto',
          borderLeft: '1px solid #FFF',
          height: '1em',
        }}
      />

      <Box
        sx={{
          mx: '0.5em',
          display: ['none', 'none', 'unset'],
          flex: '0 0 auto',
        }}
      >
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
          flex: '0 0 auto',
          borderLeft: '1px solid #FFF',
          height: '1em',
        }}
      />

      <Box
        sx={{ display: ['none', 'none', 'none', 'unset'], flex: '0 0 auto' }}
      >
        <FeedbackModal>
          <Flex sx={{ alignItems: 'center', px: '0.5em' }}>
            <Comments size="1em" style={{ marginRight: '0.5em' }} />
            <Text sx={modalLinkCSS}>Provide Feedback</Text>
          </Flex>
        </FeedbackModal>
      </Box>

      <Box
        sx={{
          flex: '0 0 auto',
          borderLeft: '1px solid #FFF',
          height: '1em',
          display: ['none', 'none', 'block'],
        }}
      />

      <Text
        sx={{
          flex: '1 1 auto',
          fontSize: 0,
          textAlign: 'right',
          ml: '0.5em',
          display: ['none', 'none', 'block'],
        }}
      >
        Created by U.S. Fish and Wildlife Service and{' '}
        <OutboundLink to="https://astutespruce.com" tabIndex={1}>
          Astute Spruce
        </OutboundLink>
      </Text>
    </Flex>
  )
}

export default Footer
