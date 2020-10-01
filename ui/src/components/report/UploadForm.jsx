import React, { useCallback, useState } from 'react'
import PropTypes from 'prop-types'
import { Button, Flex, Heading, Input, Text, Divider } from 'theme-ui'

import DropZone from './DropZone'

import { siteMetadata } from '../../../gatsby-config'

const { contactEmail } = siteMetadata

const UploadForm = ({ onFileChange, onCreateReport }) => {
  const [name, setName] = useState('')
  const [file, setFile] = useState(null)

  const handleDrop = useCallback(
    (newFile) => {
      setFile(newFile)
      onFileChange()
    },
    [onFileChange]
  )

  const handleInputChange = useCallback(({ target: { value } }) => {
    setName(value)
  }, [])

  const handleResetFile = () => {
    setFile(null)
    onFileChange()
  }

  const handleCreateReport = () => {
    onCreateReport(file, name)
  }

  return (
    <>
      <Text as="p">
        Upload a custom polygon to generate a PDF report of the Blueprint,
        underlying indicators, and landscape-level threats for your area of
        interest. If you don’t get what you expect or need help interpreting the
        results, please <a href={`mailto:${contactEmail}`}>contact us</a> -
        we&apos;re here to help!
        <br />
        <br />
        You can upload a shapefile or ESRI File Geodatabase Feature Class
        containing your area of interest, inside a zip file. Note: your zip file
        must contain only one shapefile or Feature Class, and must represent a
        relatively small area (less than several thousand acres). For help
        analyzing larger areas, please{' '}
        <a href={`mailto:${contactEmail}`}>contact us</a>.
      </Text>

      <Heading as="h3" sx={{ mt: '3rem', mb: '0.5rem' }}>
        Area Name:
      </Heading>
      <Input type="text" onChange={handleInputChange} />

      <Flex
        sx={{
          mt: '2rem',
          mb: '0.5em',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div>
          <Heading
            as="h3"
            sx={{
              mb: 0,
            }}
          >
            Choose Area of Interest:
          </Heading>
          <div>{file && <Text>{file.name}</Text>}</div>
        </div>
      </Flex>

      {file === null && <DropZone onDrop={handleDrop} />}

      {file && (
        <>
          <Divider />
          <Flex
            sx={{
              justifyContent: 'space-between',
            }}
          >
            <Button variant="secondary" onClick={handleResetFile}>
              Choose a different file
            </Button>

            <Button onClick={handleCreateReport}>Create Report</Button>
          </Flex>
        </>
      )}
    </>
  )
}

UploadForm.propTypes = {
  onFileChange: PropTypes.func.isRequired,
  onCreateReport: PropTypes.func.isRequired,
}

export default UploadForm
