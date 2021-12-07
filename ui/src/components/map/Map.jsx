// @refresh reset

import React, { useEffect, useRef, useState, useCallback, memo } from 'react'
// exclude Mapbox GL from babel transpilation per https://docs.mapbox.com/mapbox-gl-js/guides/migrate-to-v2/
/* eslint-disable-next-line */
import mapboxgl from '!mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Box } from 'theme-ui'

import { useMapData } from 'components/data'
import { useSearch } from 'components/search'
import { useBreakpoints } from 'components/layout'

import { hasWindow, isLocalDev } from 'util/dom'
import { useIsEqualEffect } from 'util/hooks'
import { getCenterAndZoom } from './util'
import { mapConfig as config, sources, layers } from './mapConfig'
import { Legend } from './legend'
import MapModeToggle from './MapModeToggle'
import StyleToggle from './StyleToggle'
import { siteMetadata } from '../../../gatsby-config'

const { mapboxToken } = siteMetadata

if (!mapboxToken) {
  // eslint-disable-next-line no-console
  console.error(
    'ERROR: Mapbox token is required in gatsby-config.js siteMetadata'
  )
}

// CSS props that control the responsive display of map widgets
const mapWidgetCSS = {
  '.mapboxgl-ctrl-zoom-in, .mapboxgl-ctrl-zoom-out, .mapboxgl-ctrl-compass': {
    display: ['none', 'inherit'],
  },
  '.mapboxgl-canvas': {
    outline: 'none',
  },
  '.mapboxgl-ctrl-attrib.mapboxgl-compact': {
    minHeight: '24px',
  },
}

const Map = () => {
  const mapNode = useRef(null)
  const mapRef = useRef(null)
  const [isLoaded, setIsLoaded] = useState(false)
  const [isBlueprintVisible, setIsBlueprintVisible] = useState(true)
  const highlightIDRef = useRef(null)
  const locationMarkerRef = useRef(null)

  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0
  const { data: mapData, setData: setMapData } = useMapData()
  const { location } = useSearch()

  useEffect(() => {
    // if there is no window, we cannot render this component
    if (!hasWindow) {
      return null
    }

    const { bounds, maxBounds, minZoom, maxZoom } = config
    const { center, zoom } = getCenterAndZoom(mapNode.current, bounds, 0.1)

    // Token must be set before constructing map
    mapboxgl.accessToken = mapboxToken

    const map = new mapboxgl.Map({
      container: mapNode.current,
      style: 'mapbox://styles/mapbox/light-v9',
      center,
      zoom,
      minZoom,
      maxZoom,
      maxBounds,
    })
    mapRef.current = map
    window.map = map // for easier debugging and querying via console

    if (!isMobile) {
      map.addControl(new mapboxgl.NavigationControl(), 'top-right')
    }

    map.on('load', () => {
      // due to styling components loading at different types, the containing
      // nodes don't always have height set; force larger view
      if (isLocalDev) {
        map.resize()
        // const { center, zoom } = getCenterAndZoom(mapNode.current, bounds, 0.1)
        // map.setZoom(zoom)
      }

      // add sources
      Object.entries(sources).forEach(([id, source]) => {
        map.addSource(id, source)
      })

      // add layers
      layers.forEach((layer) => {
        map.addLayer(layer, layer.before || null)
      })

      // update state once to trigger other components to update with map object
      setIsLoaded(() => true)
    })

    map.on('click', ({ lngLat: point }) => {
      const features = map.queryRenderedFeatures(map.project(point), {
        layers: ['unit-fill'],
      })

      if (!(features && features.length > 0)) {
        setMapData(null)
        if (isMobile) {
          map.resize()
        }
        return
      }

      const { properties } = features[0]

      // highlight selected
      map.setFilter('unit-outline-highlight', ['==', 'id', properties.id])

      setMapData(features[0].properties)
      if (isMobile) {
        map.resize()
      }
    })

    // Highlight units on mouseover
    map.on('mousemove', 'unit-fill', ({ features }) => {
      if (!map.isStyleLoaded()) {
        return
      }

      map.getCanvas().style.cursor = 'pointer'

      if (!(features && features.length > 0)) {
        return
      }

      const { id } = features[0]

      const { current: prevId } = highlightIDRef
      if (prevId !== null && prevId !== id) {
        map.setFeatureState(
          { source: 'mapUnits', sourceLayer: 'units', id: prevId },
          { highlight: false }
        )
      }
      map.setFeatureState(
        { source: 'mapUnits', sourceLayer: 'units', id },
        { highlight: true }
      )
      highlightIDRef.current = id
    })

    // Unhighlight all hover features on mouseout
    map.on('mouseout', () => {
      if (!map.isStyleLoaded()) {
        return
      }

      const { current: prevId } = highlightIDRef
      if (prevId !== null) {
        map.setFeatureState(
          { source: 'mapUnits', sourceLayer: 'units', id: prevId },
          { highlight: false }
        )
      }
    })

    // when this component is destroyed, remove the map
    return () => {
      map.remove()
    }
  }, [isMobile, setMapData])

  useIsEqualEffect(() => {
    if (!isLoaded) return
    const { current: map } = mapRef

    // sometimes map is not fully loaded on hot reload
    if (!map.loaded()) return

    if (mapData === null) {
      map.setFilter('unit-outline-highlight', ['==', 'id', Infinity])
    }
  }, [mapData, isLoaded])

  useIsEqualEffect(() => {
    if (!isLoaded) return

    if (location !== null) {
      const { current: map } = mapRef
      const { latitude, longitude } = location
      map.flyTo({ center: [longitude, latitude], zoom: 12 })

      if (locationMarkerRef.current === null) {
        locationMarkerRef.current = new mapboxgl.Marker()
          .setLngLat([longitude, latitude])
          .addTo(map)
      } else {
        locationMarkerRef.current.setLngLat([longitude, latitude])
      }
    } else if (locationMarkerRef.current !== null) {
      locationMarkerRef.current.remove()
      locationMarkerRef.current = null
    }
  }, [location, isLoaded])

  const handleToggleBlueprintVisibile = useCallback(() => {
    const { current: map } = mapRef
    if (!map) return

    setIsBlueprintVisible((prevVisible) => {
      const newIsVisible = !prevVisible
      if (newIsVisible) {
        map.setPaintProperty('blueprint', 'raster-opacity', 0.6)
      } else {
        map.setPaintProperty('blueprint', 'raster-opacity', 0)
      }
      return newIsVisible
    })
  }, [])

  // if there is no window, we cannot render this component
  if (!hasWindow) {
    return null
  }

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        flex: '1 1 auto',
        position: 'relative',
        outline: 'none',
        ...mapWidgetCSS,
      }}
    >
      <div ref={mapNode} style={{ width: '100%', height: '100%' }} />

      {!isMobile ? (
        <Legend
          isVisible={isBlueprintVisible}
          onToggleVisibility={handleToggleBlueprintVisibile}
        />
      ) : null}

      <MapModeToggle map={mapRef.current} isMobile={isMobile} />

      <StyleToggle
        map={mapRef.current}
        sources={sources}
        layers={layers}
        isMobile={isMobile}
      />
    </Box>
  )
}

// prevent rerender on props change
export default memo(Map, () => true)
