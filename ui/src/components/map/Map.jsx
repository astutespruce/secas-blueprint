// @refresh reset
/* eslint-disable no-underscore-dangle */

import React, {
  useEffect,
  useRef,
  useState,
  useCallback,
  useMemo,
  memo,
} from 'react'
// exclude Mapbox GL from babel transpilation per https://docs.mapbox.com/mapbox-gl-js/guides/migrate-to-v2/
/* eslint-disable-next-line */
import mapboxgl from '!mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { Box } from 'theme-ui'
import { MapboxLayer } from '@deck.gl/mapbox'
import { useDebouncedCallback } from 'use-debounce'

import {
  useBlueprintPriorities,
  useMapData,
  useIndicators,
} from 'components/data'
import { useBreakpoints } from 'components/layout'
import { useSearch } from 'components/search'
import { hasWindow, isLocalDev } from 'util/dom'
import { indexBy } from 'util/data'
import { useIsEqualEffect, useEventHandler } from 'util/hooks'
import CrosshairsIcon from 'images/CrosshairsIcon.svg'

import { unpackFeatureData } from './features'
import { createRenderTarget, extractPixelData, StackedPNGTileLayer } from './gl'
import { mapConfig as config, sources, layers } from './mapConfig'
import { pixelLayers, pixelLayerIndex } from './pixelLayers'
import { Legend } from './legend'
import LayerToggle from './LayerToggle'
import MapModeToggle from './MapModeToggle'
import StyleToggle from './StyleToggle'
import { getCenterAndZoom } from './viewport'

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

// layer in Mapbox Light that we want to come AFTER our layers here
const beforeLayer = 'waterway-label'

const minPixelLayerZoom = 7 // minimum reasonable zoom for getting pixel data
const minSummaryZoom = layers.filter(({ id }) => id === 'unit-outline')[0]
  .minzoom

const Map = () => {
  const mapNode = useRef(null)
  const mapRef = useRef(null)
  const {
    data: mapData,
    mapMode,
    setData: setMapData,
    renderLayer,
  } = useMapData()
  const mapModeRef = useRef(mapMode)
  const { all: blueprintInfo, categories: blueprintCategories } =
    useBlueprintPriorities()
  const blueprintColors = useMemo(
    () =>
      blueprintInfo
        .map(({ color, value }) => (value === 0 ? null : color))
        .reverse(),
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )
  const { ecosystems: ecosystemInfo, indicators: indicatorInfo } =
    useIndicators()

  const [isLoaded, setIsLoaded] = useState(false)
  const [isRenderLayerVisible, setisRenderLayerVisible] = useState(true)
  const [currentZoom, setCurrentZoom] = useState(3)
  const highlightIDRef = useRef(null)
  const locationMarkerRef = useRef(null)
  const deckGLHandler = useEventHandler(50)
  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0
  const { location } = useSearch()

  const getPixelData = useDebouncedCallback(() => {
    const { current: map } = mapRef
    if (!map) return

    if (currentZoom < minPixelLayerZoom) {
      if (mapData !== null) {
        setMapData(null)
      }
      return
    }

    const layer = map.getLayer('pixelLayers')
    // don't fetch data if layer is not yet available or is not visible
    if (
      !(
        layer &&
        layer.implementation &&
        layer.implementation.props &&
        layer.implementation.props.visible
      )
    ) {
      return
    }

    const { lng: longitude, lat: latitude } = map.getCenter()

    // If ownership isn't loaded yet, schedule a callback once tiles are loaded
    if (
      !(
        map.style._otherSourceCaches.ownership &&
        map.style._otherSourceCaches.ownership.loaded()
      )
    ) {
      setMapData({
        type: 'pixel',
        location: {
          longitude,
          latitude,
        },
        isLoading: true,
      })
      map.once('idle', getPixelData)
    }

    const pixelData = extractPixelData(
      map,
      map.getCenter(),
      layer,
      ecosystemInfo,
      indicatorInfo
    )

    if (pixelData === null) {
      // tile data not yet loaded for correct zoom, try again after next deckGL
      // render pass
      deckGLHandler.once(() => {
        getPixelData()
      })
    }

    setMapData({
      type: 'pixel',
      location: {
        longitude,
        latitude,
      },
      isLoading: pixelData === null,
      ...(pixelData || {}),
    })
  }, 10)

  useEffect(
    () => {
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
        }

        // add sources
        Object.entries(sources).forEach(([id, source]) => {
          map.addSource(id, source)
        })

        // add normal mapbox layers// add layers
        layers.forEach((layer) => {
          map.addLayer(layer, beforeLayer)
        })

        // add DeckGL pixel layer
        // by default, renders the blueprint
        const pixelLayerConfig = {
          id: 'pixelLayers',
          type: StackedPNGTileLayer,
          refinementStrategy: 'no-overlap',
          opacity: 0.7,
          filters: null,
          visible: false,
          layers: pixelLayers,
          renderTarget: createRenderTarget(
            map.painter.context.gl,
            pixelLayerIndex.blueprint,
            blueprintColors
          ),
        }

        map.addLayer(new MapboxLayer(pixelLayerConfig), beforeLayer)

        // TEMP: debug only
        // window.renderIndicator = (id) => {
        //   if (id === null) {
        //     // reset to Blueprint
        //     setRenderLayer(null)
        //     return
        //   }
        //   const [indicator] = indicatorInfo.base.indicators.filter(
        //     ({ id: indicatorId }) => indicatorId === id
        //   )
        //   if (!indicator) {
        //     return
        //   }
        //   const colors = indicator.values.map(({ color }) => color)
        //   setRenderLayer({
        //     id: indicator.id,
        //     label: indicator.label,
        //     colors,
        //     categories: indicator.values
        //       .filter(({ color }) => color !== null)
        //       .reverse(),
        //   })
        // }

        // For testing pixel mode if map is created that way
        if (mapMode === 'pixel') {
          map.setLayoutProperty('unit-fill', 'visibility', 'none')
          map.setLayoutProperty('unit-outline', 'visibility', 'none')
          map.setLayoutProperty('blueprint', 'visibility', 'none')

          map.getLayer('pixelLayers').implementation.setProps({
            visible: true,
            filters: null,
            data: { visible: true },
          })

          map.setLayoutProperty('ownership', 'visibility', 'visible')
          map.setLayoutProperty('subregions', 'visibility', 'visible')

          map.once('idle', getPixelData)
        }

        setCurrentZoom(map.getZoom())

        // enable event listener for renderer
        map.getLayer('pixelLayers').implementation.deck.setProps({
          onAfterRender: deckGLHandler.handler,
        })

        map.on('move', () => {
          if (mapModeRef.current === 'pixel') {
            getPixelData()
          }
        })

        map.on('zoomend', () => {
          if (mapModeRef.current === 'pixel') {
            getPixelData()
          }
          setCurrentZoom(map.getZoom())
        })

        // update state once to trigger other components to update with map object
        setIsLoaded(() => true)
      })

      map.on('click', ({ lngLat: point }) => {
        if (mapModeRef.current === 'pixel') {
          return
        }

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

        setMapData(unpackFeatureData(properties, ecosystemInfo, indicatorInfo))
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
    },
    // intentionally omitting getPixelData
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [isMobile, setMapData]
  )

  // handler for changed mapMode
  useEffect(
    () => {
      mapModeRef.current = mapMode

      if (!isLoaded) return
      const { current: map } = mapRef

      if (!map.isStyleLoaded()) {
        return
      }

      // toggle layer visibility
      if (mapMode === 'pixel') {
        // immediately try to retrieve pixel data if in pixel mode
        if (map.getZoom() >= minPixelLayerZoom) {
          map.once('idle', getPixelData)
        }

        map.setLayoutProperty('unit-fill', 'visibility', 'none')
        map.setLayoutProperty('unit-outline', 'visibility', 'none')
        map.setLayoutProperty('blueprint', 'visibility', 'none')

        // reset selected outline
        map.setFilter('unit-outline-highlight', ['==', 'id', Infinity])

        map.setLayoutProperty('ownership', 'visibility', 'visible')
        map.setLayoutProperty('subregions', 'visibility', 'visible')
        map.getLayer('pixelLayers').implementation.setProps({
          visible: true,
          filters: null,
          // data prop is used to force deeper reloading of tiles
          data: { visible: true },
        })
      } else {
        map.setLayoutProperty('unit-fill', 'visibility', 'visible')
        map.setLayoutProperty('unit-outline', 'visibility', 'visible')
        map.setLayoutProperty('blueprint', 'visibility', 'visible')
        map.setLayoutProperty('ownership', 'visibility', 'none')
        map.setLayoutProperty('subregions', 'visibility', 'none')

        map.getLayer('pixelLayers').implementation.setProps({
          visible: false,
          filters: null,
          data: { visible: false },
        })

        // TODO: set filtersRef to null
      }
    },

    // intentionally omitting getPixelData; it is static
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [isLoaded, mapMode]
  )

  // handler for changed mapData
  useIsEqualEffect(() => {
    if (!isLoaded) return
    const { current: map } = mapRef

    // sometimes map is not fully loaded on hot reload
    if (!map.loaded() || mapModeRef.current === 'pixel') return

    if (mapData === null) {
      map.setFilter('unit-outline-highlight', ['==', 'id', Infinity])
    }
  }, [mapData, isLoaded])

  // handler to update rendered layer
  useIsEqualEffect(() => {
    if (!isLoaded) return
    const { current: map } = mapRef

    const { id, colors } = renderLayer || {
      id: 'blueprint',
      colors: blueprintColors,
    }

    map.getLayer('pixelLayers').implementation.setProps({
      renderTarget: createRenderTarget(
        map.painter.context.gl,
        pixelLayerIndex[id],
        colors
      ),
    })
  }, [renderLayer])

  // handler for setting location
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

  const handleToggleRenderLayerVisible = useCallback(() => {
    const { current: map } = mapRef
    if (!map) return

    setisRenderLayerVisible((prevVisible) => {
      const newIsVisible = !prevVisible
      if (mapModeRef.current === 'pixel') {
        map.getLayer('pixelLayers').implementation.setProps({
          // have to toggle opacity not visibility so that pixel-level identify
          // still works
          opacity: newIsVisible ? 0.7 : 0,
        })
      } else {
        map.setLayoutProperty(
          'blueprint',
          'visibility',
          newIsVisible ? 'visible' : 'none'
        )
      }
      return newIsVisible
    })
  }, [])

  const handleBasemapChange = useCallback(
    (styleID) => {
      const { current: map } = mapRef

      if (!isLoaded) {
        return
      }

      const updateStyle = () => {
        const {
          style: {
            _layers: {
              pixelLayers: { implementation: pixelLayer },
            },
          },
        } = map

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

          // add regular layers and reapply filters / visibility
          layers.forEach((l) => {
            // make sure we're not trying to reload the same layers
            if (layerIndex[l.id]) {
              return
            }

            const layer = { ...l }

            if (mapMode === 'pixel') {
              if (
                l.id === 'blueprint' ||
                l.id === 'unit-fill' ||
                l.id === 'unit-outline'
              ) {
                layer.layout = {
                  visibility: 'none',
                }
              }
              if (l.id === 'ownership' || l.id === 'subregions') {
                layer.layout = {
                  visibility: 'visible',
                }
              }
            } else if (l.id === 'unit-outline-highlight' && mapData !== null) {
              // re-highlight selected layer
              layer.filter = ['==', 'id', mapData.id]
            }

            map.addLayer(layer, beforeLayer)
          })

          map.addLayer(pixelLayer, beforeLayer)
        })
      }

      // wait for previous to finish loading, if necessary
      if (map.isStyleLoaded()) {
        updateStyle()
      } else {
        map.once('idle', updateStyle)
      }
    },
    [isLoaded, mapData, mapMode]
  )

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

      {mapMode === 'pixel' && currentZoom >= minPixelLayerZoom ? (
        <Box
          sx={{
            position: 'absolute',
            zIndex: 0,
            left: '50%',
            top: '50%',
            ml: '-1rem',
            mt: '-1rem',
            pointerEvents: 'none',
          }}
        >
          <img
            src={CrosshairsIcon}
            style={{
              position: 'absolute',
              zIndex: 2,
              left: 0,
              top: 0,
              bottom: 0,
              right: 0,
              width: '32px',
              height: '32px',
            }}
            alt="Crosshairs icon"
          />
        </Box>
      ) : null}

      {!isMobile ? (
        <>
          <Legend
            title={
              renderLayer === null ? 'Blueprint priority' : renderLayer.label
            }
            subtitle={
              renderLayer === null
                ? 'for a connected network of lands and waters'
                : null
            }
            categories={
              renderLayer === null
                ? blueprintCategories
                : renderLayer.categories
            }
            isVisible={isRenderLayerVisible}
            onToggleVisibility={handleToggleRenderLayerVisible}
          />
          {mapMode === 'pixel' ? <LayerToggle onChange={() => {}} /> : null}
        </>
      ) : null}

      <MapModeToggle
        map={mapRef.current}
        isMobile={isMobile}
        belowMinZoom={
          mapMode === 'pixel'
            ? currentZoom < minPixelLayerZoom
            : currentZoom < minSummaryZoom
        }
      />

      <StyleToggle isMobile={isMobile} onStyleChange={handleBasemapChange} />
    </Box>
  )
}

// prevent rerender on props change
export default memo(Map, () => true)
