import React, { memo, useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

const ZoomInNote = ({ map, isMobile }) => {
  const [zoom, setZoom] = useState(0)

  useEffect(() => {
    if (!map) {
      return undefined
    }

    const updateZoom = () => {
      setZoom(map.getZoom())
    }

    map.on('zoomend', updateZoom)

    return () => {
      if (!map) return

      map.off('zoomend', updateZoom)
    }
  }, [map])

  if (zoom > 8) return null

  return (
    <Box
      sx={{
        fontSize: 0,
        position: 'absolute',
        top: 0,
        left: isMobile ? 0 : '54px',
        right: isMobile ? 0 : '54px',
        textAlign: 'center',
        py: '0.25em',
        px: '1em',
        bg: '#FFF',
        color: 'grey.7',
        borderRadius: isMobile ? null : '0 0 1em 1em',
        boxShadow: '0 2px 6px #666',
      }}
    >
      <Text sx={{ mx: 'auto' }}>Zoom in to select an area</Text>
    </Box>
  )
}

ZoomInNote.propTypes = {
  map: PropTypes.object,
  isMobile: PropTypes.bool,
}

ZoomInNote.defaultProps = {
  map: null,
  isMobile: false,
}

export default memo(ZoomInNote)
