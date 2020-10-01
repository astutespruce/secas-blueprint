import React from 'react'
import { Container, Box, Heading } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

const UnsupportedBrowser = () => (
  <Container>
    <Box
      sx={{
        m: '2rem',
        p: '2rem',
        background: 'primary',
      }}
    >
      <Heading as="h2">
        <ExclamationTriangle size="2rem" style={{ marginRight: '.5rem' }} />
        Unfortunately, you are using an unsupported version of Internet
        Explorer.
        <br />
        <br />
        Please use a modern browser such as Google Chrome, Firefox, or Microsoft
        Edge.
      </Heading>
    </Box>
  </Container>
)

export default UnsupportedBrowser
