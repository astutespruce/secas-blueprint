import React, { useState, useCallback, useRef, memo } from 'react'
import PropTypes from 'prop-types'
import { Box, Image } from 'theme-ui'

import { indexBy } from 'util/data'

import LightIcon from 'images/light-v9.jpg'
import SatelliteIcon from 'images/satellite-streets-v11.jpg'

const coreCSS = {
  cursor: 'pointer',
  position: 'absolute',
  zIndex: 999,
  overflow: 'hidden',
}

const desktopCSS = {
  ...coreCSS,
  left: '10px',
  bottom: '40px',
  borderRadius: '64px',
  border: '2px solid #FFF',
  boxShadow: '0 1px 5px rgba(0, 0, 0, 0.65)',
  width: '64px',
  height: '64px',
}

const mobileCSS = {
  ...coreCSS,
  right: '10px',
  top: '24px',
  width: '40px',
  height: '40px',
  borderRadius: '32px',
  boxShadow: '0 1px 5px #000',
  border: '1px solid #FFF',
}

const styles = [
  { id: 'light-v9', label: 'Light Basemap', icon: LightIcon },
  {
    id: 'satellite-streets-v11',
    label: 'Satellite Basemap',
    icon: SatelliteIcon,
  },
]

const StyleToggle = ({ isMobile, onStyleChange }) => {
  const [index, setIndex] = useState(0)

  const handleToggle = () => {
    setIndex((prevIndex) => {
      const nextIndex = prevIndex === 0 ? 1 : 0
      onStyleChange(styles[nextIndex].id)
      return nextIndex
    })
  }

  const { label, icon } = styles[index === 0 ? 1 : 0]

  return (
    <Box sx={isMobile ? mobileCSS : desktopCSS}>
      <Image
        sx={{ height: '100%', width: '100%' }}
        alt={label}
        src={icon}
        onClick={handleToggle}
      />
    </Box>
  )
}

StyleToggle.propTypes = {
  onStyleChange: PropTypes.func.isRequired,
  isMobile: PropTypes.bool,
}

StyleToggle.defaultProps = {
  isMobile: false,
}

export default memo(StyleToggle)
