import React, { memo, useCallback, useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Text, Flex, Button } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { useMapData } from 'components/data'

const baseCSS = {
  position: 'absolute',
  textAlign: 'center',
  pt: '0.75em',
  pb: '0.5em',
  px: '1em',
  bg: '#FFF',
  color: 'grey.7',
  boxShadow: '0 2px 6px #666',
}

const mobileCSS = {
  ...baseCSS,
  fontSize: 0,
  left: 0,
  right: 0,
  bottom: 0,
  zIndex: 1000,
}

const desktopCSS = {
  ...baseCSS,

  fontSize: 1,
  left: '12px',
  top: 0,
  borderRadius: '0 0 1em 1em',
}

// Note: zoom is not updated on initial render because map hasn't yet rendered,
// this assumes zoom is for full extent
const MapModeToggle = ({ map, isMobile }) => {
  const [zoom, setZoom] = useState(0)
  const { data: mapData, mapMode, setMapMode } = useMapData()

  useEffect(() => {
    if (!map) {
      return undefined
    }

    // set initial value
    setZoom(map.getZoom())

    const updateZoom = () => {
      setZoom(map.getZoom())
    }

    map.on('zoomend', updateZoom)

    return () => {
      if (!map) return

      map.off('zoomend', updateZoom)
    }
  }, [map])

  const handlePixelClick = useCallback(() => {
    setMapMode('pixel')
  }, [setMapMode])

  const handleUnitClick = useCallback(() => {
    setMapMode('unit')
  }, [setMapMode])

  if (isMobile && mapData !== null) {
    return null
  }

  const showZoomNote = zoom < 7

  return (
    <Box sx={isMobile ? mobileCSS : desktopCSS}>
      <Flex
        sx={{
          alignItems: 'center',
          flexWrap: 'wrap',
          justifyContent: isMobile ? 'center' : null,
        }}
      >
        <Flex
          sx={{
            alignItems: 'center',
          }}
        >
          <Text sx={{ mr: '0.5rem' }}>Show:</Text>
          <Button
            variant="group"
            data-state={mapMode === 'pixel' ? 'active' : null}
            onClick={handlePixelClick}
          >
            Pixel data
          </Button>
          <Button
            variant="group"
            data-state={mapMode === 'unit' ? 'active' : null}
            onClick={handleUnitClick}
          >
            Summary data
          </Button>
        </Flex>

        {showZoomNote ? (
          <Flex
            sx={{
              alignItems: 'center',
              ml: '1rem',
              color: 'accent',
            }}
          >
            <ExclamationTriangle size="16px" style={{ marginRight: '.5rem' }} />
            <Text>
              Zoom in to select {mapMode === 'pixel' ? 'a pixel' : 'an area'}
            </Text>
          </Flex>
        ) : null}

        {!showZoomNote && mapMode === 'pixel' ? (
          <Text
            sx={{ fontSize: 0, textAlign: 'left', ml: '0.5rem', lineHeight: 1 }}
          >
            Pan the map behind the crosshairs <br /> to show details in sidebar
          </Text>
        ) : null}
      </Flex>
    </Box>
  )
}

MapModeToggle.propTypes = {
  map: PropTypes.object,
  isMobile: PropTypes.bool,
}

MapModeToggle.defaultProps = {
  map: null,
  isMobile: false,
}

export default memo(MapModeToggle)
