import React from 'react'
import PropTypes from 'prop-types'
import { Alert, Close, Box, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { OutboundLink } from 'components/link'
import config from '../../../gatsby-config'

const { contactEmail } = config.siteMetadata

const UploadError = ({ error, handleClearError }) => {
  return (
    <Alert variant="error" sx={{ mt: '2rem', mb: '4rem', py: '1rem' }}>
      <ExclamationTriangle
        size="2rem"
        style={{
          margin: '0 1rem 0 0',
        }}
      />
      <Box>
        Uh oh! There was an error!
        <br />
        {error ? (
          `The server says: ${error}`
        ) : (
          <>
            <Text as="span">
              Please try again. If that does not work, try a different file or
            </Text>{' '}
            <OutboundLink
              sx={{ color: '#FFF' }}
              href={`mailto:${contactEmail}`}
            >
              Contact Us
            </OutboundLink>
            .
          </>
        )}
      </Box>
      <Close
        variant="buttons.alertClose"
        ml="auto"
        onClick={handleClearError}
      />
    </Alert>
  )
}

UploadError.propTypes = {
  error: PropTypes.string,
  handleClearError: PropTypes.func.isRequired,
}

UploadError.defaultProps = {
  error: null,
}

export default UploadError
