import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import {
  Box,
  Button,
  Flex,
  Heading,
  Input,
  Text,
  Divider,
  Grid,
  Image,
} from 'theme-ui'
import { FormProvider, useForm } from 'react-hook-form'

import { ContactModal } from 'components/modal'
import { OutboundLink } from 'components/link'

import Thumbnail1 from 'images/report/report_sm_1.png'
import Thumbnail2 from 'images/report/report_sm_2.png'
import Thumbnail3 from 'images/report/report_sm_3.png'
import Thumbnail4 from 'images/report/report_sm_4.png'
import Thumbnail5 from 'images/report/report_sm_5.png'

import DropZone from './DropZone'

const linkCSS = {
  display: 'inline-block',
  color: 'link',
  cursor: 'pointer',
  '&:hover': { textDecoration: 'underline' },
}

const UploadForm = ({ onFileChange, onCreateReport }) => {
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

  const handleSubmit = useCallback(
    (values) => {
      const { areaName, file: fileProp } = values

      onCreateReport(fileProp, areaName)
    },
    [onCreateReport]
  )

  const handleResetFile = () => {
    setValue('file', null)
    onFileChange()
  }

  return (
    <>
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(handleSubmit)}>
          <Grid columns={[0, 2]} gap={5} sx={{ mt: '2rem' }}>
            <Box>
              <Heading as="h3" sx={{ mb: '0.5rem' }}>
                Area Name (optional):
              </Heading>
              <Input
                type="text"
                name="areaName"
                {...register('areaName', { required: false })}
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
            </Box>

            <Text as="p">
              Upload a shapefile or ESRI File Geodatabase Feature Class
              containing your area of interest to generate a detailed PDF report
              of the Blueprint, underlying indicators, and landscape-level
              threats for your area of interest. It includes a map and summary
              table for every indicator present in the area, as well as
              additional information about urbanization and sea-level rise.
              <br />
              <br />
              Don&apos;t have a shapefile? You can create one using{' '}
              <OutboundLink to="https://geojson.io/#map=6/32.861/-81.519">
                geojson.io
              </OutboundLink>{' '}
              to draw your area of interest, save as a shapefile, then upload
              here.
              <br />
              <br />
              <ContactModal>
                <Text sx={linkCSS}>
                  <b>We are here</b>
                </Text>
              </ContactModal>{' '}
              to help you interpret and apply this information to your
              particular application!
              <br />
              <br />
              You can help us improve the Blueprint and this report by helping
              us understand your use case: we use this information to provide
              statistics about how the Blueprint is being used and to prioritize
              improvements.
              <br />
              <br />
              Note: your files must be in a zip file, and can include only one
              shapefile or Feature Class, and must represent a relatively small
              area (full extent must be less than 5 million acres). For help
              analyzing larger areas, please{' '}
              <ContactModal>
                <Text sx={linkCSS}>contact us</Text>
              </ContactModal>
              .
            </Text>
          </Grid>
        </form>
      </FormProvider>

      <Box
        sx={{
          mt: '2rem',
          borderTop: '1px solid',
          borderTopColor: 'grey.3',
          pt: '2rem',
          mb: '4rem',
        }}
      >
        <Heading as="h3">Examples of what is inside</Heading>
        <Grid
          columns={5}
          sx={{
            mt: '1rem',
            img: {
              width: '250px',
              border: '1px solid',
              borderColor: 'grey.4',
              boxShadow: `1px 1px 3px #000`,
            },
          }}
        >
          <Image src={Thumbnail1} />
          <Image src={Thumbnail2} />
          <Image src={Thumbnail3} />
          <Image src={Thumbnail4} />
          <Image src={Thumbnail5} />
        </Grid>
        <Text as="p" sx={{ mt: '1rem' }}>
          ...and much more!
        </Text>
      </Box>
    </>
  )
}

UploadForm.propTypes = {
  onFileChange: PropTypes.func.isRequired,
  onCreateReport: PropTypes.func.isRequired,
}

export default UploadForm
