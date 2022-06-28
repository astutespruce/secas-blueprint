/* eslint-disable no-alert */
import React, { useCallback, useEffect } from 'react'
import PropTypes from 'prop-types'
import { useDropzone } from 'react-dropzone'
import { useFormContext } from 'react-hook-form'
import { Flex, Heading, Text } from 'theme-ui'
import { transparentize } from '@theme-ui/color'
import { Download } from '@emotion-icons/fa-solid'

const MAXSIZE_MB = 100

const DropZone = ({ name }) => {
  const { register, unregister, setValue } = useFormContext()

  /**
   * Register the file drop input; this must be done in useEffect since
   * it is dynamically constructed.
   */
  useEffect(() => {
    register(name, { required: true })
    return () => {
      unregister(name)
    }
  }, [register, unregister, name])

  /**
   * Validate the files provided by the user.
   * They must be only one file, must be right MIME type and be less than the
   * maximum size.
   */
  const handleDrop = useCallback(
    (acceptedFiles, rejectedFiles) => {
      if (rejectedFiles && rejectedFiles.length > 0) {
        if (rejectedFiles.length > 1) {
          alert(
            `Multiple files not allowed: ${rejectedFiles
              .map(({ file: { name: filename } }) => filename)
              .join(', ')}`
          )
          return
        }

        const {
          file: { name: filename },
          size,
        } = rejectedFiles[0]

        console.log('filename is', rejectedFiles[0])

        const mb = size / 1e6
        if (mb >= MAXSIZE_MB) {
          alert(
            `File is too large: ${filename} (${Math.round(
              mb
            ).toLocaleString()} MB)`
          )
          return
        }

        alert(`File type not supported: ${filename}`)
        return
      }

      if (acceptedFiles && acceptedFiles.length > 0) {
        setValue(name, acceptedFiles[0], { shouldValidate: true })
      }
    },
    [name, setValue]
  )

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject,
  } = useDropzone({
    onDrop: handleDrop,
    accept: {
      'application/zip': [],
      'application/x-zip-compressed': [],
      'application/x-compressed': [],
      'multipart/x-zip': [],
    },
    maxSize: MAXSIZE_MB * 1e6,
    multiple: false,
  })

  let color = 'grey.5'
  if (isDragAccept) {
    color = 'ok'
  } else if (isDragReject) {
    color = 'error'
  }

  return (
    <Flex
      sx={{
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Flex
        // {...getRootProps({ isDragActive, isDragAccept, isDragReject })}
        {...getRootProps()}
        sx={{
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          width: '100%',
          p: '2rem',
          cursor: 'pointer',
          outline: 'none',
          borderWidth: '2px',
          borderStyle: 'dashed',
          borderRadius: '1rem',
          borderColor: color,
          backgroundColor: transparentize(color, 0.9),
        }}
      >
        <input name={name} {...getInputProps()} />
        <Download size="32px" style={{ marginBottom: '1rem' }} />
        <Heading as="h3" sx={{ mb: '1rem' }}>
          Drop your zip file here
        </Heading>
        <Text as="p" sx={{ color: 'grey.7', textAlign: 'center', fontSize: 1 }}>
          Zip file must contain all associated files for a shapefile (at least
          .shp, .prj, .shx) or file geodatabase (.gdb).
          <br />
          <br />
          Max size: {MAXSIZE_MB} MB.
        </Text>
      </Flex>
    </Flex>
  )
}

DropZone.propTypes = {
  name: PropTypes.string.isRequired,
}

export default DropZone
