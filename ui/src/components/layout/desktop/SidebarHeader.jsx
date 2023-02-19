import React, { useState, useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Flex, Heading, Text } from 'theme-ui'
import { TimesCircle } from '@emotion-icons/fa-regular'
import { Download } from '@emotion-icons/fa-solid'

import { useMapData } from 'components/data'
import { DownloadModal } from 'components/report'
import { formatNumber } from 'util/format'

const SidebarHeader = ({ type, id, name, location, acres, onClose }) => {
  const { mapMode, filters, resetFilters } = useMapData()
  const numFilters = Object.values(filters).filter(
    ({ enabled }) => enabled
  ).length

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
            <Flex sx={{ justifyContent: 'space-between' }}>
              <Text sx={{ color: 'grey.9', fontSize: 2, flex: '1 1 auto' }}>
                Coordinates: {location.latitude.toPrecision(5)}°N,{' '}
                {location.longitude.toPrecision(5)}°
              </Text>
              <Box
                sx={{
                  flex: '0 0 auto',
                  justifyContent: 'flex-end',
                  alignItems: 'center',
                  visibility: numFilters > 0 ? 'visible' : 'hidden',
                  mr: '-1.5rem',
                }}
              >
                <Button
                  onClick={resetFilters}
                  sx={{ fontSize: 0, py: '0.2em', bg: 'accent', px: '0.5rem' }}
                >
                  <Flex sx={{ alignItems: 'center' }}>
                    <Box sx={{ mr: '0.25em' }}>
                      <TimesCircle size="1em" />
                    </Box>
                    <Text>
                      reset {numFilters} pixel filter{numFilters > 1 ? 's' : ''}
                    </Text>
                  </Flex>
                </Button>
              </Box>
            </Flex>
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

        {type !== 'pixel' ? (
          <Button
            variant="close"
            onClick={onClose}
            sx={{ flex: '0 0 auto', margin: 0, padding: 0 }}
          >
            <TimesCircle size="1.5em" />
          </Button>
        ) : null}
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
          <Download size="16px" style={{ marginRight: '0.5rem' }} />
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
