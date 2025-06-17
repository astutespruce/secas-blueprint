<script lang="ts">
	import { getContext } from 'svelte'

	import { MapboxOverlay } from '@deck.gl/mapbox'
	// TODO: debounced callback; svelte alternative to use-debounce

	import CrosshairsIcon from '$images/CrosshairsIcon.svg'
	import Spinner from '~icons/fa-solid/spinner'

	import {
		ecosystems as ecosystemInfo,
		indicators as indicatorInfo,
		subregionIndex
	} from '$lib/config/constants'
	import type { MapData } from '$lib/types'
	import { indexBy } from '$lib/util/data'
	import { debounce, eventHandler } from '$lib/util/func'

	import { unpackFeatureData } from './features'
	import FindLocation from './FindLocation.svelte'
	import { extractPixelData, StackedPNGTileLayer } from './gl'
	import { Legend } from './legend'
	import { mapConfig as config, sources, layers } from '$lib/config/map'
	import { mapboxgl } from './mapbox'
	import { pixelLayers, renderLayersIndex } from '$lib/config/pixelLayers'
	import LayerToggle from './LayerToggle.svelte'
	import MapModeToggle from './MapModeToggle.svelte'
	import StyleToggle from './StyleToggle.svelte'
	import { getCenterAndZoom } from './viewport'

	let map: mapboxgl.Map
	const mapData: MapData = getContext('map-data')
	const { data, mapMode, renderLayer, filters, setData, setVisibleSubregions } = mapData

	let isLoaded: boolean = $state(false)
	let isRenderLayerVisible: boolean = $state(true)
	let currentZoom: number = $state(3)
	let highlightId: number | string | undefined = $state()

	// mapIsDrawing is used to show the spinner; it only gets set via a deounced callback to prevent short duration flashes
	let mapIsDrawing: boolean = $state(false)
	// delayedMapIsDrawing is toggled immediately when map enters drawing state and is used in callback to determine if should toggle mapIsDrawing
	let delayedMapIsDrawing: boolean = $state(false)

	// TODO: location from search

	const deckGLHandler = eventHandler(50)
	const updateMapIsDrawing = debounce(() => {
		mapIsDrawing = delayedMapIsDrawing
	}, 1500)

	// layer in Mapbox Light that we want to come AFTER our layers here
	const beforeLayer = 'waterway-label'

	const minPixelLayerZoom = 7 // minimum reasonable zoom for getting pixel data
	const minSummaryZoom = layers.filter(({ id }) => id === 'unit-outline')[0].minzoom

	const setPixelLayerProps = (map, newProps) => {
		if (!map) return

		// this happens in hot reload
		if (!(map && map.__deck && map.__deck.layerManager)) return

		/* eslint-disable-next-line no-underscore-dangle */
		map.__deck.setProps({
			layers: [
				/* eslint-disable-next-line no-underscore-dangle */
				map.__deck.layerManager.layers[0].clone(newProps)
			]
		})
	}

	const getPixelData = () => {
		// TODO: implement
	}

	const updateVisibleSubregions = () => {
		// TODO: implement
	}

	const hideGulfOfMexico = () => {
		if (map === null) {
			return
		}
		// hide Gulf of Mexico
		if (map.style._layers['marine-label-md-pt']) {
			map.setFilter('marine-label-md-pt', [
				'all',
				['==', '$type', 'Point'],
				['in', 'labelrank', 2, 3],
				['!=', 'name', 'Gulf of Mexico']
			])
		} else if (map.style._layers['water-point-label']) {
			map.setFilter('water-point-label', [
				'all',
				[
					'match',
					['get', 'class'],
					// remove 'sea'; this category includes the gulf
					['ocean', 'reservoir', 'water'],
					true,
					false
				],
				['==', ['geometry-type'], 'Point']
			])
		}
	}

	const createMap = (mapNode: HTMLDivElement) => {
		const { bounds, maxBounds, minZoom, maxZoom } = config
		const { center, zoom } = getCenterAndZoom(mapNode, bounds, 0)

		map = new mapboxgl.Map({
			container: mapNode,
			style: 'mapbox://styles/mapbox/light-v9',
			center,
			zoom,
			minZoom,
			maxZoom,
			maxBounds
		})

		// @ts-ignore
		window.map = map // for easier debugging and querying via console

		map.addControl(new mapboxgl.NavigationControl(), 'top-right')

		map.on('style.load', hideGulfOfMexico)

		map.on('load', () => {
			// FIXME: remove
			// due to styling components loading at different times, the containing
			// nodes don't always have height set; force larger view
			// if (isLocalDev) {
			// 	map.resize()
			// }

			// add sources
			Object.entries(sources).forEach(([id, source]) => {
				// @ts-ignore
				map.addSource(id, source)
			})

			// add DeckGL pixel layer
			// by default, renders the blueprint
			const deckGLOverlay = new MapboxOverlay({
				interleaved: true,

				layers: [
					new StackedPNGTileLayer({
						id: 'pixelLayers',
						// interleaved: true,
						beforeId: beforeLayer,
						refinementStrategy: 'no-overlap',
						debounceTime: 10, // slightly debounce tile requests during major zoom / pan events
						layers: pixelLayers,
						extent: bounds,
						maxRequests: 20, // because these are on HTTP/2, we can fetch many at once
						opacity: 0.7,
						filters: null,
						visible: false,
						renderLayer,
						tileSize: 512
					})
				]
			})
			map.addControl(deckGLOverlay)

			map.once('idle', () => {
				// update state once to trigger other components to update with map object
				isLoaded = true
			})

			// add normal mapbox layers// add layers
			layers.forEach((layer) => {
				// @ts-ignore
				map.addLayer(layer, beforeLayer)
			})

			// if map is initialized in pixel or filter mode
			if (mapMode === 'pixel' || mapMode === 'filter') {
				map.setLayoutProperty('unit-fill', 'visibility', 'none')
				map.setLayoutProperty('unit-outline', 'visibility', 'none')
				map.setLayoutProperty('blueprint', 'visibility', 'none')

				setPixelLayerProps(map, {
					visible: true,
					filters: null,
					data: { visible: true }
				})

				map.setLayoutProperty('protectedAreas', 'visibility', 'visible')
				map.setLayoutProperty('subregions', 'visibility', 'visible')

				map.once('idle', getPixelData)
			}

			// enable event listener for renderer
			if (mapMode === 'pixel') {
				// @ts-ignore
				map.getLayer('pixelLayers')!.deck!.setProps({
					onAfterRender: deckGLHandler.handler
				})
			}

			currentZoom = map.getZoom()

			map.on('move', () => {
				if (mapData.mapMode === 'pixel') {
					getPixelData()
				}
			})

			map.on('moveend', () => {
				delayedMapIsDrawing = true
				if (mapData.mapMode === 'filter') {
					updateVisibleSubregions()
				}
				updateMapIsDrawing()
			})

			map.on('zoomend', () => {
				if (mapData.mapMode === 'pixel') {
					getPixelData()
				} else if (mapData.mapMode === 'filter') {
					updateVisibleSubregions()
				}
				currentZoom = map.getZoom()
			})
		})

		map.on('idle', () => {
			mapIsDrawing = false
			delayedMapIsDrawing = false
		})

		map.on('click', ({ lngLat: point }) => {
			if (mapData.mapMode === 'pixel') {
				return
			}

			const features = map.queryRenderedFeatures(map.project(point), {
				layers: ['unit-fill']
			})

			if (!(features && features.length > 0)) {
				mapData.data = null
				// TODO: resize on mobile
				// if (isMobile) {
				// 	map.resize()
				// }
				return
			}

			const { properties } = features[0]

			// highlight selected
			map.setFilter('unit-outline-highlight', ['==', 'id', properties!.id])

			mapData.data = unpackFeatureData(properties, ecosystemInfo, indicatorInfo, subregionIndex)
			// TODO: resize on mobile
			// if (isMobile) {
			// 	map.resize()
			// }
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

			if (highlightId !== undefined && highlightId !== id) {
				map.setFeatureState(
					// @ts-ignore
					{ source: 'mapUnits', sourceLayer: 'units', id: highlightId },
					{ highlight: false }
				)
			}
			// @ts-ignore
			map.setFeatureState({ source: 'mapUnits', sourceLayer: 'units', id }, { highlight: true })
			highlightId = id
		})

		// Unhighlight all hover features on mouseout
		map.on('mouseout', () => {
			if (!map.isStyleLoaded()) {
				return
			}

			if (highlightId !== undefined) {
				map.setFeatureState(
					// @ts-ignore
					{ source: 'mapUnits', sourceLayer: 'units', id: highlightId },
					{ highlight: false }
				)
			}
			highlightId = undefined
		})

		// when this component is destroyed, remove the map
		return () => {
			map?.remove()
		}
	}

	// TODO: effects for changed map mode, mapData, etc

	const handleToggleRenderLayerVisible = () => {
		if (!map) return
		isRenderLayerVisible = !isRenderLayerVisible
		if (mapData.mapMode === 'unit') {
			map.setLayoutProperty('blueprint', 'visibility', isRenderLayerVisible ? 'visible' : 'none')
		} else {
			// have to toggle opacity not visibility so that pixel-level identify
			// still works
			setPixelLayerProps(map, { opacity: isRenderLayerVisible ? 0.7 : 0 })
		}
	}

	const handleBasemapChange = (styleID: string) => {
		if (!(map && isLoaded)) {
			return
		}

		const updateStyle = () => {
			const pixelLayer = map!.getLayer('pixelLayers')

			map!.setStyle(`mapbox://styles/mapbox/${styleID}`)

			map!.once('style.load', () => {
				hideGulfOfMexico()

				const {
					sources: styleSources,
					layers: styleLayers,
					// @ts-ignore
					metadata: { 'mapbox:origin': curStyleId }
				} = map!.getStyle()
				const layerIndex = indexBy(styleLayers, 'id')

				if (curStyleId === 'satellite-streets-v11') {
					// make satellite a bit more washed out
					map!.setPaintProperty('background', 'background-color', '#FFF')
					map!.setPaintProperty('satellite', 'raster-opacity', 0.75)
				}

				// add sources back
				Object.entries(sources).forEach(([id, source]) => {
					// make sure we're not trying to reload the same style, which already has these
					if (!styleSources[id]) {
						// @ts-ignore
						map!.addSource(id, source)
					}
				})

				// add regular layers and reapply filters / visibility
				layers.forEach((l) => {
					// make sure we're not trying to reload the same layers
					if (layerIndex[l.id]) {
						return
					}

					const layer = { ...l }

					if (mapMode !== 'unit') {
						if (l.id === 'blueprint' || l.id === 'unit-fill' || l.id === 'unit-outline') {
							layer.layout = {
								visibility: 'none'
							}
						}
						if (l.id === 'protectedAreas' || l.id === 'subregions') {
							layer.layout = {
								visibility: 'visible'
							}
						}
					} else {
						if (l.id === 'blueprint' && !isRenderLayerVisible) {
							layer.layout = {
								visibility: 'none'
							}
						}
						if (l.id === 'unit-outline-highlight' && mapData !== null) {
							// re-highlight selected layer
							layer.filter = ['==', 'id', data.id]
						}
					}

					// @ts-ignore
					map!.addLayer(layer, beforeLayer)
				})

				if (!map!.getLayer('pixelLayers')) {
					// pixel layer appears to now be retained on style change
					// @ts-ignore
					map!.addLayer(pixelLayer, beforeLayer)
				}
			})
		}

		// wait for previous to finish loading, if necessary
		if (map.isStyleLoaded()) {
			updateStyle()
		} else {
			map.once('idle', updateStyle)
		}
	}

	const belowMinZoom = $derived(
		mapData.mapMode === 'pixel'
			? currentZoom < minPixelLayerZoom
			: currentZoom < (minSummaryZoom || 0)
	)

	const displayLayer = $derived(
		mapData.mapMode === 'unit' ? renderLayersIndex.blueprint : mapData.renderLayer
	)
</script>

<div class="h-full w-full flex-auto relative">
	<div class="h-full w-full" {@attach createMap}></div>

	{#if mapIsDrawing}
		<div
			class="absolute left-0 top-0 bottom-0 right-0 bg-grey-0/50 flex justify-center items-center"
		>
			<Spinner class="size-6 animate-spin" />
		</div>
	{/if}

	{#if mapMode === 'pixel' && currentZoom >= minPixelLayerZoom}
		<img
			src={CrosshairsIcon}
			alt="Crosshairs icon"
			class="absolute block z-0 right-0 bottom-0 left-[50%] top-[50%] ml-[-1rem] mt-[-1rem] pointer-events-none size-8"
		/>
	{/if}

	{#if isLoaded}
		<Legend
			title={displayLayer.label}
			subtitle={displayLayer.valueLabel}
			categories={displayLayer.categories}
			isVisible={isRenderLayerVisible}
			onToggleLayerVisibility={handleToggleRenderLayerVisible}
		/>
		<!--
		{#if mapMode !== 'unit'}
			<LayerToggle />
		{/if}

		<FindLocation />

		<MapModeToggle {map} {isMobile} {belowMinZoom} /> -->

		<StyleToggle onChange={handleBasemapChange} />
	{/if}
</div>
