import { browser } from '$app/environment'
import { TILE_HOST } from '$lib/env'
import type { MapConfig } from '$lib/types'

export let tileHost = TILE_HOST

if (browser && !tileHost) {
	tileHost = `//${window.location.host}`
}

export const mapConfig: MapConfig = {
	// NOTE: these are not the data bounds, but ideal bounds to leave enough room
	// east of Puerto Rico for the legend
	// bounds: [-106.93611462308955, 14.65662961734786, -48.85555906753385, 43.47207027673693],
	// FIXME:
	bounds: [-90.48508728921513, 31.26228744904597, -89.39964140377695, 31.899777691031517],

	maxBounds: [-180, -80, 180, 80],
	minZoom: 3,
	maxZoom: 14
}

export const sources = {
	blueprint: {
		type: 'raster',
		// tiles are at 512, but using 256 forces higher resolution
		tileSize: 256,
		minzoom: 3,
		maxzoom: 14,
		bounds: [-108.0227, 16.97285, -57.03082, 41.58111],
		tiles: [`${tileHost}/services/blueprint/tiles/{z}/{x}/{y}.png`]
	},
	mapUnits: {
		type: 'vector',
		minzoom: 3,
		maxzoom: 14,
		bounds: [-180, -85, 180, 85],
		tiles: [`${tileHost}/services/se_map_units/tiles/{z}/{x}/{y}.pbf`],
		// note: can use promoteId: 'id' to promote feature properties ID to feature ID
		promoteId: 'id'
	},
	pixelFeatures: {
		type: 'vector',
		minzoom: 3,
		maxzoom: 14,
		bounds: [-106.655273, 17.623082, -64.423828, 40.647304],
		tiles: [`${tileHost}/services/se_other_features/tiles/{z}/{x}/{y}.pbf`]
	}
}

export const layers = [
	// protected areas and subregions are added with no fill in order to detect features in pixel mode
	{
		id: 'protectedAreas',
		source: 'pixelFeatures',
		'source-layer': 'protectedAreas',
		type: 'fill',
		minzoom: 5,
		layout: {
			visibility: 'none'
		},
		paint: {
			'fill-color': '#FFF',
			'fill-opacity': 0
		}
	},
	{
		id: 'subregions',
		source: 'pixelFeatures',
		'source-layer': 'subregions',
		type: 'fill',
		minzoom: 3,
		layout: {
			visibility: 'none'
		},
		paint: {
			'fill-color': '#FFF',
			'fill-opacity': 0
		}
	},
	{
		id: 'blueprint',
		source: 'blueprint',
		type: 'raster',
		minzoom: 3,
		paint: {
			'raster-opacity': 0.7
		}
	},
	{
		id: 'se-boundary-outline',
		source: 'mapUnits',
		'source-layer': 'boundary',
		minzoom: 3,
		maxzoom: 14,
		type: 'line',
		paint: {
			'line-color': '#000',
			'line-width': {
				stops: [
					[6, 1],
					[8, 0.1]
				]
			}
		}
	},

	{
		id: 'unit-fill',
		source: 'mapUnits',
		'source-layer': 'units',
		minzoom: 8,
		type: 'fill',
		paint: {
			'fill-color': '#0892D0',
			'fill-opacity': ['case', ['boolean', ['feature-state', 'highlight'], false], 0.3, 0]
		}
	},
	{
		id: 'unit-outline',
		source: 'mapUnits',
		'source-layer': 'units',
		minzoom: 8,
		type: 'line',
		paint: {
			'line-opacity': 1,
			'line-color': '#000',
			'line-width': ['interpolate', ['linear'], ['zoom'], 8, 0.25, 10, 1, 13, 4]
		}
	},
	{
		id: 'unit-outline-highlight',
		source: 'mapUnits',
		'source-layer': 'units',
		type: 'line',
		filter: ['==', 'id', Infinity],
		paint: {
			'line-opacity': 1,
			'line-color': '#000000',
			'line-width': {
				stops: [
					[8, 3],
					[12, 6]
				]
			}
		}
	}
]
