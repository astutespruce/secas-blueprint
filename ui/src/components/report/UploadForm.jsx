import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import { graphql, useStaticQuery } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'
import {
  Box,
  Button,
  Flex,
  Heading,
  Label,
  Input,
  Text,
  Divider,
  Grid,
  Paragraph,
} from 'theme-ui'
import { FormProvider, useForm } from 'react-hook-form'

import { ContactModal } from 'components/modal'
import { OutboundLink } from 'components/link'

import DropZone from './DropZone'

const linkCSS = {
  display: 'inline-block',
  color: 'link',
  cursor: 'pointer',
  '&:hover': { textDecoration: 'underline' },
}

const UploadForm = ({ onFileChange, onCreateReport }) => {
  const {
    reportImage1: {
      childImageSharp: { gatsbyImageData: reportImage1 },
    },
    reportImage2: {
      childImageSharp: { gatsbyImageData: reportImage2 },
    },
    reportImage3: {
      childImageSharp: { gatsbyImageData: reportImage3 },
    },
    reportImage4: {
      childImageSharp: { gatsbyImageData: reportImage4 },
    },
    reportImage5: {
      childImageSharp: { gatsbyImageData: reportImage5 },
    },
  } = useStaticQuery(graphql`
    query {
      reportImage1: file(relativePath: { eq: "report/report_sm_1.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: CONSTRAINED
            formats: [AUTO, WEBP]
            placeholder: BLURRED
            width: 180
          )
        }
      }
      reportImage2: file(relativePath: { eq: "report/report_sm_2.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: CONSTRAINED
            formats: [AUTO, WEBP]
            placeholder: BLURRED
            width: 180
          )
        }
      }
      reportImage3: file(relativePath: { eq: "report/report_sm_3.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: CONSTRAINED
            formats: [AUTO, WEBP]
            placeholder: BLURRED
            width: 180
          )
        }
      }
      reportImage4: file(relativePath: { eq: "report/report_sm_4.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: CONSTRAINED
            formats: [AUTO, WEBP]
            placeholder: BLURRED
            width: 180
          )
        }
      }
      reportImage5: file(relativePath: { eq: "report/report_sm_5.png" }) {
        childImageSharp {
          gatsbyImageData(
            layout: CONSTRAINED
            formats: [AUTO, WEBP]
            placeholder: BLURRED
            width: 180
          )
        }
      }
    }
  `)

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
              <Box>
                <Label
                  htmlFor="areaName"
                  sx={{ mb: '0.5rem', fontWeight: 'bold', fontSize: [3, 4] }}
                >
                  Area Name (optional):
                </Label>
                <Input
                  type="text"
                  id="areaName"
                  name="areaName"
                  {...register('areaName', { required: false })}
                />
              </Box>

              <Flex
                sx={{
                  mt: '2rem',
                  mb: '0.5em',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <Label
                    htmlFor="file"
                    sx={{
                      mb: 0,
                      fontWeight: 'bold',
                      fontSize: [3, 4],
                    }}
                  >
                    Choose Area of Interest:
                  </Label>
                  <div>{file && <Text>{file.name}</Text>}</div>
                </div>
              </Flex>

              <Box sx={{ display: file ? 'none' : 'block' }}>
                <DropZone name="file" id="file" />
              </Box>

              <Box
                sx={{ fontSize: 0, color: 'grey.8', px: '1rem', mt: '0.5rem' }}
              >
                Note: your files must be in a zip file, and can include only one
                shapefile or Feature Class, and should represent a relatively
                small area. For help analyzing larger areas, please{' '}
                <ContactModal>
                  <Text sx={linkCSS}>contact us</Text>
                </ContactModal>
                .
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

            <Paragraph>
              Upload a zipped shapefile or ESRI File Geodatabase Feature Class
              containing your area of interest to generate a detailed PDF report
              of the Blueprint, underlying indicators, and other contextual
              information for your area of interest. It includes a map and
              summary table for every indicator present in the area, as well as
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
              We are working on resolving some technical challenges to make
              these these automatically generated reports more accessible to
              people with disabilities. In the meantime, to request an
              accessible PDF or other assistance, please contact Hilary Morris
              at{' '}
              <a href="mailto:hilary_morris@fws.gov">
                hilary_morris@fws.gov
              </a>.
              <br />
              <br />
              You can help us improve the Blueprint and this report by helping
              us understand your use case: we use this information to provide
              statistics about how the Blueprint is being used and to prioritize
              improvements.
            </Paragraph>
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
              width: '178px',
              border: '1px solid',
              borderColor: 'grey.4',
            },
          }}
        >
          <GatsbyImage
            image={reportImage1}
            alt="Tool report example screenshot 1"
          />
          <GatsbyImage
            image={reportImage2}
            alt="Tool report example screenshot 2"
          />
          <GatsbyImage
            image={reportImage3}
            alt="Tool report example screenshot 3"
          />
          <GatsbyImage
            image={reportImage4}
            alt="Tool report example screenshot 4"
          />
          <GatsbyImage
            image={reportImage5}
            alt="Tool report example screenshot 5"
          />
        </Grid>
        <Paragraph sx={{ mt: '1rem' }}>...and much more!</Paragraph>
      </Box>
    </>
  )
}

UploadForm.propTypes = {
  onFileChange: PropTypes.func.isRequired,
  onCreateReport: PropTypes.func.isRequired,
}

export default UploadForm
