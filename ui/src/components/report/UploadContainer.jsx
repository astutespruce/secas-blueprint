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
  CheckCircle,
  Download,
  ExclamationTriangle,
} from '@emotion-icons/fa-solid'
import { Clock } from '@emotion-icons/fa-regular'

import { OutboundLink } from 'components/link'
import { captureException, logGAEvent } from 'util/log'
import { uploadFile } from './api'
import UploadForm from './UploadForm'
import UploadError from './UploadError'
import config from '../../../gatsby-config'

const { contactEmail } = config.siteMetadata

const UploadContainer = () => {
  const [
    {
      reportURL,
      status,
      progress,
      queuePosition,
      elapsedTime,
      message,
      errors,
      error,
      inProgress,
    },
    setState,
  ] = useState({
    reportURL: null,
    status: null,
    progress: 0,
    queuePosition: 0,
    elapsedTime: null,
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
      queuePosition: 0,
      elapsedTime: null,
      message: null,
      errors: null,
      error: null,
      reportURL: null,
    }))

    logGAEvent('create-custom-report', {
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
          status: nextStatus,
          progress: nextProgress,
          queuePosition: nextQueuePosition,
          elapsedTime: nextElapsedTime,
          message: nextMessage = null,
          errors: nextErrors = null,
        }) => {
          setState(
            ({ message: prevMessage, errors: prevErrors, ...prevState }) => ({
              ...prevState,
              status: nextStatus,
              inProgress:
                nextStatus === 'in_progress' ||
                (nextStatus === 'queued' && nextElapsedTime < 5),
              progress: nextProgress,
              queuePosition: nextQueuePosition,
              elapsedTime: nextElapsedTime,
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
          status: null,
          progress: 0,
          queuePosition: 0,
          elapsedTime: null,
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
        status: null,
        progress: 100,
        queuePosition: 0,
        elapsedTime: null,
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
        status: null,
        progress: 0,
        queuePosition: 0,
        elapsedTime: null,
        message: null,
        errors: null,
        error: '', // no meaningful error to show to user, but needs to be non-null
      }))
    }
  }, [])

  const handleReset = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      status: null,
      progress: 0,
      queuePosition: 0,
      elapsedTime: null,
      reportURL: null,
      error: null,
    }))
  }, [])

  if (error !== null) {
    return (
      <Container sx={{ py: '2rem' }}>
        <UploadError error={error} handleClearError={handleReset} />
        <Divider />
        <Flex sx={{ justifyContent: 'center' }}>
          <Button onClick={handleReset}>Try again?</Button>
        </Flex>
      </Container>
    )
  }

  if (reportURL !== null) {
    return (
      <Container sx={{ py: '2rem' }}>
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
      </Container>
    )
  }

  if (inProgress) {
    return (
      <Container sx={{ py: '2rem' }}>
        <Heading as="h3" sx={{ mb: '0.5rem' }}>
          {message ? `${message}...` : 'Creating report...'}
        </Heading>

        <Flex sx={{ alignItems: 'center' }}>
          <Progress variant="styles.progress" max={100} value={progress} />
          <Text sx={{ ml: '1rem' }}>{progress}%</Text>
        </Flex>
      </Container>
    )
  }

  if (status === 'queued') {
    return (
      <Container sx={{ py: '2rem' }}>
        <Flex
          sx={{ alignItems: 'center', gap: '1rem', mt: '1rem', mb: '0.5rem' }}
        >
          <Box sx={{ color: 'grey.9' }}>
            <Clock size="2rem" />
          </Box>
          <Heading as="h2">
            {message
              ? `${message}...`
              : 'Waiting for other jobs to complete...'}
          </Heading>
        </Flex>

        <Text sx={{ fontSize: 3 }}>
          The server is currently working on reports that have already been
          submitted and it will start working on your report as soon as
          possible.
          <br />
          <br />
          {queuePosition > 0
            ? `Waiting on ${queuePosition} other report${queuePosition > 1 ? 's' : ''} to complete`
            : 'Your report is next in line'}
          .
          <br />
          <br />
          {elapsedTime !== null
            ? `You have been waiting for ${Math.floor(elapsedTime / 60)} minutes and ${(elapsedTime - Math.floor(elapsedTime / 60) * 60).toString().padStart(2, '0')} seconds.`
            : null}
        </Text>
      </Container>
    )
  }

  return (
    <Container sx={{ py: '2rem' }}>
      <UploadForm
        onFileChange={handleReset}
        onCreateReport={handleCreateReport}
      />
    </Container>
  )
}

export default UploadContainer
