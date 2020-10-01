import React, { useState, useCallback } from 'react'
import {
  Box,
  Container,
  Divider,
  Heading,
  Flex,
  Link,
  Progress,
  Text,
} from 'theme-ui'
import { Download, CheckCircle } from '@emotion-icons/fa-solid'

import { captureException } from 'util/log'
import { uploadFile } from './api'
import UploadForm from './UploadForm'
import UploadError from './UploadError'

const UploadContainer = () => {
  const [{ reportURL, progress, error, inProgress }, setState] = useState({
    reportURL: null,
    progress: 0,
    inProgress: false,
    error: null, // if error is non-null, it indicates there was an error
  })

  const handleCreateReport = useCallback(async (file, name) => {
    // clear out previous progress and errors
    setState((prevState) => ({
      ...prevState,
      inProgress: true,
      progress: 0,
      error: null,
      reportURL: null,
    }))

    try {
      // upload file and update progress
      const { error: uploadError, result } = await uploadFile(
        file,
        name,
        (nextProgress) => {
          setState((prevState) => ({ ...prevState, progress: nextProgress }))
        }
      )

      if (uploadError) {
        // eslint-disable-next-line no-console
        console.error(uploadError)

        setState((prevState) => ({
          ...prevState,
          inProgress: false,
          progress: 0,
          error: uploadError,
        }))
        return
      }

      // upload and processing completed successfully
      setState((prevState) => ({
        ...prevState,
        progress: 100,
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
        error: '', // no meaningful error to show to user, but needs to be non-null
      }))
    }
  }, [])

  const handleClearError = useCallback(() => {
    setState((prevState) => ({ ...prevState, error: null }))
  }, [])

  return (
    <Container sx={{ py: '2rem' }}>
      {reportURL != null && (
        <Box sx={{ mb: '6rem' }}>
          <Heading as="h2" sx={{ mb: '0.5rem' }}>
            <CheckCircle
              size="1em"
              style={{
                marginRight: '0.5rem',
              }}
            />
            All done!
          </Heading>
          <Text>
            Your report is now complete. It should download automatically.
            <br />
            <br />
            You can also click the link below to download your report.
          </Text>

          <Link href={reportURL} target="_blank">
            <Download size="1em" style={{ marginRight: '0.5rem' }} />
            Download report
          </Link>

          <Divider />

          <Text>You can also create another report below.</Text>
        </Box>
      )}

      {inProgress ? (
        <>
          <Heading as="h2" sx={{ mb: '0.5rem' }}>
            Creating report...
          </Heading>

          <Flex sx={{ alignItems: 'center' }}>
            <Progress variant="styles.progress" max={100} value={progress} />
            <Text sx={{ ml: '1rem' }}>{progress}%</Text>
          </Flex>
        </>
      ) : (
        <>
          {error != null ? (
            <UploadError error={error} handleClearError={handleClearError} />
          ) : null}

          <UploadForm
            onFileChange={handleClearError}
            onCreateReport={handleCreateReport}
          />
        </>
      )}
    </Container>
  )
}

export default UploadContainer
