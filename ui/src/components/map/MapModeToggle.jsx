import React, { memo, useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Text, Flex } from 'theme-ui'
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
  const { data: mapData, mapMode } = useMapData()

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

  if (isMobile && mapData !== null) {
    return null
  }

  const showZoomNote = zoom < 8

  if (!showZoomNote) {
    return null
  }

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
            ml: '1rem',
            color: 'accent',
          }}
        >
          <ExclamationTriangle size="1rem" style={{ marginRight: '.5rem' }} />
          <Text>
            Zoom in to select {mapMode === 'pixel' ? 'a pixel' : 'an area'}
          </Text>
        </Flex>
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
