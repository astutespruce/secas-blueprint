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

const StyleToggle = ({ map, sources, layers, mapMode, isMobile }) => {
  const [index, setIndex] = useState(0)
  const styleRef = useRef(null)

  const handleBasemapChange = useCallback(
    (styleID) => {
      if (!map) {
        return
      }

      // save as a ref since this might be called several times in series,
      // and we want to make sure we grab the latest
      styleRef.current = map.getStyle()

      const updateStyle = () => {
        const visibility = {
          pixel: mapMode === 'pixel',
          summary: mapMode !== 'pixel',
        }

        map.setStyle(`mapbox://styles/mapbox/${styleID}`)

        map.once('style.load', () => {
          const {
            sources: styleSources,
            layers: styleLayers,
            metadata: { 'mapbox:origin': curStyleId },
          } = map.getStyle()
          const layerIndex = indexBy(styleLayers, 'id')

          if (curStyleId === 'satellite-streets-v11') {
            // make satellite a bit more washed out
            map.setPaintProperty('background', 'background-color', '#FFF')
            map.setPaintProperty('satellite', 'raster-opacity', 0.75)
          }

          // add sources back
          Object.entries(sources).forEach(([id, source]) => {
            // make sure we're not trying to reload the same style, which already has these
            if (!styleSources[id]) {
              map.addSource(id, source)
            }
          })

          // add layers and reapply filters
          layers.forEach((l) => {
            // make sure we're not trying to reload the same layers
            if (layerIndex[l.id]) {
              return
            }

            const layer = { ...l }

            if (l.id === 'unit-outline-highlight') {
              const [prevLyr] = styleRef.current.layers.filter(
                ({ id }) => id === 'unit-outline-highlight'
              )

              if (prevLyr) {
                layer.filter = prevLyr.filter
              }
            }

            // set layer visibility for map mode
            if (layer.mode) {
              layer.layout = {
                visibility: visibility[layer.mode] ? 'visible' : 'none',
              }
            }

            map.addLayer(layer, layer.before || null)
          })
        })
      }

      // wait for previous to finish loading, if necessary
      if (map.isStyleLoaded()) {
        updateStyle()
      } else {
        map.once('idle', updateStyle)
      }
    },
    [map, layers, mapMode, sources]
  )

  const handleToggle = () => {
    setIndex((prevIndex) => {
      const nextIndex = prevIndex === 0 ? 1 : 0
      handleBasemapChange(styles[nextIndex].id)
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
  map: PropTypes.object,
  sources: PropTypes.objectOf(
    PropTypes.shape({ type: PropTypes.string.isRequired })
  ).isRequired,
  layers: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      paint: PropTypes.object,
    })
  ).isRequired,
  mapMode: PropTypes.string.isRequired,
  isMobile: PropTypes.bool,
}

StyleToggle.defaultProps = {
  map: null,
  isMobile: false,
}

export default memo(StyleToggle)
