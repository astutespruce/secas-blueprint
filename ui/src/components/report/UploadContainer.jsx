import React, { useState, useCallback } from 'react'
import {
  Box,
  Button,
  Container,
  Divider,
  Heading,
  Flex,
  Link,
  Progress,
  Text,
  Paragraph,
} from 'theme-ui'
import {
  Download,
  CheckCircle,
  ExclamationTriangle,
} from '@emotion-icons/fa-solid'

import { OutboundLink } from 'components/link'
import { captureException, logGAEvent } from 'util/log'
import { uploadFile } from './api'
import UploadForm from './UploadForm'
import UploadError from './UploadError'
import config from '../../../gatsby-config'

const { contactEmail } = config.siteMetadata

const UploadContainer = () => {
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

  const handleCreateReport = useCallback(async (file, name) => {
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

    logGAEvent('create-report', {
      name,
      file: file.name,
      sizeKB: file.size / 1024,
    })

    try {
      // upload file and update progress
      const {
        error: uploadError,
        result,
        errors: finalErrors,
      } = await uploadFile(
        file,
        name,
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

        logGAEvent('file-upload-error')

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
      captureException('File upload failed', ex)
      // eslint-disable-next-line no-console
      console.error('Caught unhandled error from uploadFile', ex)

      setState((prevState) => ({
        ...prevState,
        inProgress: false,
        progress: 0,
        message: null,
        errors: null,
        error: '', // no meaningful error to show to user, but needs to be non-null
      }))
    }
  }, [])

  const handleReset = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      progress: 0,
      reportURL: null,
      error: null,
    }))
  }, [])

  return (
    <Container sx={{ py: '2rem' }}>
      {reportURL != null ? (
        <Box sx={{ mb: '6rem' }}>
          <Heading as="h3" sx={{ mb: '0.5rem' }}>
            <CheckCircle
              size="1em"
              style={{
                marginRight: '0.5rem',
              }}
            />
            All done!
          </Heading>

          <Text>
            {errors && errors.length > 0 ? (
              <Text
                sx={{
                  display: 'block',
                  mt: '1rem',
                  color: 'error',
                  ul: {
                    ml: '1rem',
                  },
                  'ul li': {
                    fontSize: '2',
                    color: 'error',
                  },
                }}
              >
                <ExclamationTriangle
                  size="16px"
                  style={{
                    margin: '0 0.5rem 0 0',
                    display: 'inline',
                  }}
                />
                <Paragraph sx={{ color: 'error', display: 'inline' }}>
                  Unfortunately, the server had an unexpected error creating
                  your report. It was able to create most of your report, but
                  some sections may be missing. The server says:
                  <br />
                </Paragraph>

                <ul>
                  {errors.map((e) => (
                    <li key={e}>{e}</li>
                  ))}
                </ul>
                <br />
                <Paragraph>
                  Please try again. If that does not work, please{' '}
                  <OutboundLink href={`mailto:${contactEmail}`}>
                    contact us
                  </OutboundLink>
                  .
                </Paragraph>
              </Text>
            ) : null}

            <Paragraph>
              <br />
              <br />
              Your report should download automatically. You can also click the
              link below to download your report.
              <br />
              <br />
              <Link href={reportURL} target="_blank">
                <Download size="1.5em" style={{ marginRight: '0.5rem' }} />
                Download report
              </Link>
            </Paragraph>
          </Text>

          <Divider />

          <Flex sx={{ justifyContent: 'center' }}>
            <Button onClick={handleReset}>Create another report?</Button>
          </Flex>
        </Box>
      ) : (
        <>
          {inProgress ? (
            <>
              <Heading as="h3" sx={{ mb: '0.5rem' }}>
                {message ? `${message}...` : 'Creating report...'}
              </Heading>

              <Flex sx={{ alignItems: 'center' }}>
                <Progress
                  variant="styles.progress"
                  max={100}
                  value={progress}
                />
                <Text sx={{ ml: '1rem' }}>{progress}%</Text>
              </Flex>
            </>
          ) : (
            <>
              {error != null ? (
                <>
                  <UploadError error={error} handleClearError={handleReset} />
                  <Divider />
                  <Flex sx={{ justifyContent: 'center' }}>
                    <Button onClick={handleReset}>Try again?</Button>
                  </Flex>
                </>
              ) : (
                <UploadForm
                  onFileChange={handleReset}
                  onCreateReport={handleCreateReport}
                />
              )}
            </>
          )}
        </>
      )}
    </Container>
  )
}

export default UploadContainer
