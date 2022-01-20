import React, { useState, useCallback } from 'react'
import PropTypes from 'prop-types'
import {
  Alert,
  Box,
  Divider,
  Flex,
  Link,
  Button,
  Progress,
  Text,
} from 'theme-ui'
import {
  Download,
  CheckCircle,
  ExclamationTriangle,
} from '@emotion-icons/fa-solid'

import { OutboundLink } from 'components/link'
import { captureException } from 'util/log'
import { Modal } from 'components/modal'
import { createSummaryUnitReport } from './api'
import config from '../../../gatsby-config'

const { contactEmail } = config.siteMetadata

const DownloadModal = ({ id, type, onClose }) => {
  const [
    { reportURL, progress, message, errors, error, inProgress },
    setState,
  ] = useState({
    reportURL: null,
    progress: 0,
    message: null,
    errors: null, // non-fatal errors
    inProgress: false,
    error: null, // if error is non-null, it indicates there was an error
  })

  const handleClose = useCallback(() => {
    setState(() => ({
      reportURL: null,
      error: null,
      progress: 0,
      message: null,
      errors: null,
      inProgress: false,
    }))
    onClose()
  }, [onClose])

  const handleCreateReport = useCallback(async () => {
    // clear out previous progress and errors
    setState((prevState) => ({
      ...prevState,
      inProgress: true,
      progress: 0,
      message: null,
      errors: null,
      error: null,
      reportURL: null,
    }))

    try {
      const {
        error: uploadError,
        result,
        errors: finalErrors,
      } = await createSummaryUnitReport(
        id,
        type,
        ({
          progress: nextProgress,
          message: nextMessage = null,
          errors: nextErrors = null,
        }) => {
          setState(
            ({ message: prevMessage, errors: prevErrors, ...prevState }) => ({
              ...prevState,
              progress: nextProgress,
              message: nextMessage || prevMessage,
              errors: nextErrors || prevErrors,
            })
          )
        }
      )

      if (uploadError) {
        // eslint-disable-next-line no-console
        console.error(uploadError)

        setState((prevState) => ({
          ...prevState,
          inProgress: false,
          progress: 0,
          message: null,
          errors: null,
          error: uploadError,
        }))
        return
      }

      // upload and processing completed successfully
      setState((prevState) => ({
        ...prevState,
        progress: 100,
        message: null,
        errors: finalErrors, // there may be non-fatal errors (e.g., errors rendering maps)
        inProgress: false,
        reportURL: result,
      }))

      window.location.href = result
    } catch (ex) {
      captureException(`Create summary report for ${id} (${type}) failed`, ex)
      // eslint-disable-next-line no-console
      console.error('Caught unhandled error from createSummaryUnitReport', ex)

      setState((prevState) => ({
        ...prevState,
        inProgress: false,
        progress: 0,
        error: '', // no meaningful error to show to user, but needs to be non-null
      }))
    }
  }, [id, type])

  let content = null

  if (reportURL !== null) {
    content = (
      <Box sx={{ py: '1rem' }}>
        <Text as="h3" sx={{ fontWeight: 'bold', mb: '0.5rem' }}>
          <CheckCircle
            size="1em"
            style={{
              marginRight: '0.5rem',
            }}
          />
          All done!
        </Text>
        <Text>
          {errors && errors.length > 0 ? (
            <Text
              sx={{
                mt: '1rem',
                color: 'error',
                ul: {
                  mt: '0.5em',
                  ml: '1em',
                },
                'ul li': {
                  color: 'error',
                },
              }}
            >
              <ExclamationTriangle
                size="16px"
                style={{
                  margin: '0 0.5rem 0 0',
                }}
              />
              Unfortunately, the server had an unexpected error creating your
              report. It was able to create most of your report, but some
              sections may be missing. The server says:
              <br />
              <ul>
                {errors.map((e) => (
                  <li key={e}>{e}</li>
                ))}
              </ul>
              <br />
              Please try again. If that does not work, please{' '}
              <OutboundLink to={`mailto:${contactEmail}`}>
                Contact Us
              </OutboundLink>
              .
            </Text>
          ) : null}
          <br />
          <br />
          Your report should download automatically. You can also click the
          button below to download your report.
        </Text>
      </Box>
    )
  } else if (error !== null) {
    content = (
      <Alert variant="error" sx={{ mt: '1rem', mb: '1rem', py: '1rem' }}>
        <ExclamationTriangle
          size="32px"
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
                Please try again. If that does not work, please
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
      </Alert>
    )
  } else if (inProgress) {
    content = (
      <Box sx={{ py: '2rem' }}>
        <Text>{message ? `${message}...` : 'Creating report...'}</Text>

        <Flex sx={{ alignItems: 'center' }}>
          <Progress variant="styles.progress" max={100} value={progress} />
          <Text sx={{ ml: '1rem' }}>{progress}%</Text>
        </Flex>
      </Box>
    )
  } else {
    content = (
      <Text sx={{ p: '1rem' }}>
        Create and download a Blueprint summary report for this area. This
        detailed report includes maps and analysis of the Blueprint priorities
        and each indicator present in this area, as well as potential threats
        and information about land ownership and partners.
      </Text>
    )
  }

  return (
    <Modal title="Blueprint Summary Report" onClose={handleClose}>
      {content}

      <Divider sx={{ my: '0.5rem' }} />
      <Flex sx={{ justifyContent: 'space-between' }}>
        <Button variant="secondary" onClick={handleClose}>
          Cancel
        </Button>

        {reportURL ? (
          <Link href={reportURL} target="_blank">
            <Button>
              <Flex sx={{ alignItems: 'center' }}>
                <Download size="1em" style={{ marginRight: '0.5rem' }} />
                Download report
              </Flex>
            </Button>
          </Link>
        ) : (
          <>
            {!(inProgress || error) ? (
              <Button onClick={handleCreateReport}>Create report</Button>
            ) : null}
          </>
        )}
      </Flex>
    </Modal>
  )
}

DownloadModal.propTypes = {
  id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  type: PropTypes.oneOf(['subwatershed', 'marine lease block']).isRequired,
  onClose: PropTypes.func.isRequired,
}

export default DownloadModal
