import React, { useState, useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Flex, Heading, Text } from 'theme-ui'
import { TimesCircle } from '@emotion-icons/fa-regular'
import { Download } from '@emotion-icons/fa-solid'

import { DownloadModal } from 'components/report'
import { formatNumber } from 'util/format'

const SidebarHeader = ({ type, id, name, location, acres, onClose }) => {
  const [isReportModalOpen, setIsReportModalOpen] = useState(false)

  const handleReportModalClose = useCallback(() => {
    setIsReportModalOpen(() => false)
  }, [])

  const handleReportModalOpen = useCallback(() => {
    setIsReportModalOpen(() => true)
  }, [])

  return (
    <>
      <Flex
        sx={{
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          p: '1rem',
          minHeight: type === 'pixel' ? null : '7rem',
        }}
      >
        <Box sx={{ mr: '1rem', flex: '1 1 auto' }}>
          {type === 'pixel' ? (
            <Text sx={{ textAlign: 'center', color: 'grey.8' }}>
              Coordinates: {location.latitude.toPrecision(5)}°N,{' '}
              {location.longitude.toPrecision(5)}°
            </Text>
          ) : (
            <Heading as="h3">
              {name}

              {type === 'subwatershed' ? (
                <Text
                  as="span"
                  sx={{
                    fontSize: 0,
                    fontWeight: 'normal',
                    ml: '0.5em',
                    display: 'inline-block',
                  }}
                >
                  (HUC12)
                </Text>
              ) : null}
            </Heading>
          )}
          {acres !== null ? (
            <Text sx={{ color: 'grey.6', fontSize: [0, 1] }}>
              {formatNumber(acres)} acres
            </Text>
          ) : null}
        </Box>

        <Button
          variant="close"
          onClick={onClose}
          sx={{ flex: '0 0 auto', margin: 0, padding: 0 }}
        >
          <TimesCircle size="1.5em" />
        </Button>
      </Flex>

      {type !== 'pixel' ? (
        <Flex
          sx={{
            px: '1rem',
            pb: '0.5rem',
            alignItems: 'center',
            color: 'primary',
            cursor: 'pointer',
            '&:hover': {
              textDecoration: 'underline',
            },
          }}
          onClick={handleReportModalOpen}
        >
          <Download size="1rem" style={{ marginRight: '0.5rem' }} />
          <Text>Export detailed maps and analysis</Text>
        </Flex>
      ) : null}

      {isReportModalOpen ? (
        <DownloadModal id={id} type={type} onClose={handleReportModalClose} />
      ) : null}
    </>
  )
}

SidebarHeader.propTypes = {
  type: PropTypes.string.isRequired,
  id: PropTypes.string,
  name: PropTypes.string,
  acres: PropTypes.number,
  location: PropTypes.shape({
    latitude: PropTypes.number.isRequired,
    longitude: PropTypes.number.isRequired,
  }),
  onClose: PropTypes.func.isRequired,
}

SidebarHeader.defaultProps = {
  id: null,
  name: null,
  acres: null,
  location: null,
}

export default SidebarHeader
