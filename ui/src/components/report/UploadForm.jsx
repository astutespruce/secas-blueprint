import React, { useCallback, useEffect } from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Flex, Heading, Input, Text, Divider } from 'theme-ui'
import { FormProvider, useForm } from 'react-hook-form'

import { getFromStorage } from 'util/dom'

import DropZone from './DropZone'
import UserInfoForm from './UserInfoForm'

import { siteMetadata } from '../../../gatsby-config'

const { contactEmail } = siteMetadata

const UploadForm = ({ onFileChange, onCreateReport, onSubmitUserInfo }) => {
  const methods = useForm({
    mode: 'onBlur',
  })

  const {
    formState: { isValid },
    register,
    watch,
    setValue,
  } = methods

  const file = watch('file', null)

  useEffect(() => {
    const savedUserInfo = getFromStorage('reportForm')
    if (savedUserInfo) {
      Object.entries(savedUserInfo).forEach(([field, value]) => {
        setValue(field, value)
      })
    }
  }, [setValue])

  const handleSubmit = useCallback(
    (values) => {
      const { areaName, file: fileProp, ...userInfo } = values

      onCreateReport(fileProp, areaName)

      // only submit user info if it is non-empty
      if (Object.values(userInfo).filter((v) => v).length > 0) {
        onSubmitUserInfo({ ...userInfo, areaName, fileName: fileProp.name })
      }
    },
    [onCreateReport, onSubmitUserInfo]
  )

  const handleResetFile = () => {
    setValue('file', null)
    onFileChange()
  }

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(handleSubmit)}>
        <Text as="p">
          Upload a custom polygon to generate a PDF report of the Blueprint,
          underlying indicators, and landscape-level threats for your area of
          interest. If you don’t get what you expect or need help interpreting
          the results, please <a href={`mailto:${contactEmail}`}>contact us</a>{' '}
          - we&apos;re here to help!
          <br />
          <br />
          You can upload a shapefile or ESRI File Geodatabase Feature Class
          containing your area of interest, inside a zip file. Note: your zip
          file must contain only one shapefile or Feature Class, and must
          represent a relatively small area (full extent must be less than 3
          million acres). For help analyzing larger areas, please{' '}
          <a href={`mailto:${contactEmail}`}>contact us</a>.
        </Text>

        <Heading as="h3" sx={{ mt: '3rem', mb: '0.5rem' }}>
          Area Name (optional):
        </Heading>
        <Input
          type="text"
          name="areaName"
          ref={register({ required: false })}
        />

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

        <Box sx={{ display: file ? 'none' : 'block' }}>
          <DropZone name="file" />
        </Box>

        <UserInfoForm />

        <Divider />
        <Flex
          sx={{
            justifyContent: 'space-between',
          }}
        >
          <Button
            variant="secondary"
            onClick={handleResetFile}
            sx={{ visibility: file ? 'visible' : 'hidden' }}
          >
            Choose a different file
          </Button>

          <Button
            as="button"
            type="submit"
            variant={isValid ? 'primary' : 'disabled'}
            disabled={!isValid}
          >
            Create Report
          </Button>
        </Flex>
      </form>
    </FormProvider>
  )
}

UploadForm.propTypes = {
  onFileChange: PropTypes.func.isRequired,
  onCreateReport: PropTypes.func.isRequired,
  onSubmitUserInfo: PropTypes.func.isRequired,
}

export default UploadForm
