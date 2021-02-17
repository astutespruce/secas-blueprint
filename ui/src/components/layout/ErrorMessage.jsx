import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Text, Container } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { OutboundLink } from 'components/link'
import { siteMetadata } from '../../../gatsby-config'

const ErrorMessage = ({ message }) => (
  <Container sx={{ py: '4rem' }}>
    <Box>
      <Heading as="h2" sx={{ mb: '1rem' }}>
        <ExclamationTriangle size="2rem" style={{ marginRight: '.5rem' }} />
        Whoops! Something went wrong...
      </Heading>
      <Text sx={{ fontSize: 3, color: 'grey.9' }}>
        We&apos;re sorry, something didn&apos;t quite work properly.
        <br />
        <br />
        Please try to refresh this page. If the error continues, please{' '}
        <OutboundLink to={`mailto:${siteMetadata.contactEmail}`}>
          let us know
        </OutboundLink>
        .
      </Text>
      {message && (
        <Text
          sx={{
            mt: '1rem',
            pt: '1rem',
            borderTop: '1px solid',
            borderTopColor: 'grey.2',
          }}
        >
          <Heading as="h3">Details</Heading>
          <Text>{message}</Text>
        </Text>
      )}
    </Box>
  </Container>
)

ErrorMessage.propTypes = {
  message: PropTypes.string,
}

ErrorMessage.defaultProps = {
  message: null,
}

export default ErrorMessage
