import { indexBy, sortByFunc } from '$lib/util/data'
import type {
	Indicator,
	PixelLayerBounds,
	PixelLayerEncodings,
	PixelLayerIndex,
	PixelLayer
} from '$lib/types'

import {
	blueprint,
	blueprintCategories,
	corridors,
	ecosystems,
	indicatorsIndex,
	urban,
	slrDepth,
	slrNodata,
	wildfireRisk,
	protectedAreas,
	pixelLayers0,
	pixelLayers1,
	pixelLayers2,
	pixelLayers3,
	pixelLayers4,
	pixelLayers5,
	pixelLayers6,
	pixelLayers7,
	pixelLayers8
} from './constants'

import { tileHost } from './map'

const pixelLayerEncoding: PixelLayerEncodings = {
	0: pixelLayers0,
	1: pixelLayers1,
	2: pixelLayers2,
	3: pixelLayers3,
	4: pixelLayers4,
	5: pixelLayers5,
	6: pixelLayers6,
	7: pixelLayers7,
	8: pixelLayers8
}

// this is copy-pasted from bounds reported by the tile services
const pixelLayerBounds: PixelLayerBounds = {
	0: [-108.0227, 16.97285, -57.03082, 41.58111],
	1: [-108.0227, 23.73322, -74.0301, 41.58035],
	2: [-98.53344, 22.37943, -70.38168, 40.66711],
	3: [-108.0227, 22.4353, -70.06457, 41.58092],
	4: [-108.0227, 23.78806, -74.172, 41.58053],
	5: [-98.26575, 17.10476, -57.73155, 40.36863],
	6: [-67.97848, 16.97285, -64.29697, 19.34715],
	7: [-67.97848, 16.97285, -64.29697, 19.34715],
	8: [-108.0227, 16.98923, -57.08541, 41.58111]
}

const pixelLayerSourceConfig = { tileSize: 512, minzoom: 3, maxzoom: 14 }

export const pixelLayers = [...Array(9).keys()].map((i) => ({
	...pixelLayerSourceConfig,
	id: `pixels${i}`,
	url: `${tileHost}/services/se_pixel_layers_${i}/tiles/{z}/{x}/{y}.png`,
	bounds: pixelLayerBounds[i],
	encoding: pixelLayerEncoding[i]
}))

// create index of encoded layers
export const pixelLayerIndex: PixelLayerIndex = {}
pixelLayers.forEach(({ encoding }, textureIndex) => {
	encoding.forEach(({ id, bits, offset, valueShift }) => {
		pixelLayerIndex[id] = { textureIndex, bits, offset, valueShift }
	})
})

const coreLayers: PixelLayer[] = [
	{
		id: 'blueprint',
		label: 'Blueprint priority',
		valueLabel: 'for a connected network of lands and waters', // used in legend
		// sort colors in ascending value; blueprint is in descending order
		colors: blueprint.map(({ color, value }) => (value === 0 ? null : color)).reverse(),
		categories: blueprintCategories,
		layer: pixelLayerIndex.blueprint
	},
	{
		id: 'corridors',
		label: 'Hubs and corridors',
		colors: corridors
			.slice()
			.sort(sortByFunc('value'))
			.map(({ color }) => color),
		categories: corridors
			.filter(({ value }) => value > 0)
			.map(({ value, label, color }) => ({
				value,
				label,
				color
				// type: 'fill'
			})),
		layer: pixelLayerIndex.corridors
	}
]

const otherInfoLayers: PixelLayer[] = [
	{
		id: 'urban',
		label: 'Probability of urbanization by 2060',
		colors: urban.map(({ color }) => color),
		categories: urban.map(({ color, ...rest }) => ({
			...rest,
			color: color || '#FFFFFF',
			outlineWidth: 1,
			outlineColor: 'grey.5'
		})),
		layer: pixelLayerIndex.urban
	},
	{
		id: 'slr',
		label: 'Flooding extent by projected sea-level rise',
		colors: slrDepth.concat(slrNodata).map(({ color }) => color),
		categories: slrDepth
			.concat(slrNodata.filter(({ value }) => value !== 13))
			.map(({ label, ...rest }, i) => ({
				...rest,
				label:
					/* eslint-disable-next-line no-nested-ternary */
					i === 1 ? `${label} foot` : i <= 10 ? `${label} feet` : label,
				outlineWidth: 1,
				outlineColor: 'grey.5'
			})),
		layer: pixelLayerIndex.slr
	},
	{
		id: 'wildfireRisk',
		label: 'Wildfire likelihood (annual burn probability)',
		colors: wildfireRisk.map(({ color }) => color),
		// sort in descending order
		// NOTE: this uses a custom legend for simple label values, not the full
		// set of categories
		categories: Object.values(
			Object.fromEntries(
				wildfireRisk
					.map(({ label, color, ...rest }) => ({
						label: label.split(' (')[0],
						color: color || '#FFFFFF',
						outlineWidth: 1,
						outlineColor: 'grey.5',
						...rest
					}))
					.map((item) => [item.label, item])
					.reverse()
			)
		),
		layer: pixelLayerIndex.wildfireRisk
	},
	{
		id: 'protectedAreas',
		label: 'Protected areas',
		colors: protectedAreas.map(({ color }) => color),
		categories: protectedAreas.filter(({ color }) => color !== null),
		layer: pixelLayerIndex.protectedAreas
	}
]

const layers = coreLayers.concat(otherInfoLayers)

export const renderLayerGroups = [
	{
		id: 'core',
		label: 'Priorities',
		layers: coreLayers
	}
]

ecosystems.forEach(({ id: groupId, label: groupLabel, indicators: groupIndicators }) => {
	const group = {
		id: groupId,
		label: `${groupLabel} indicators`,
		layers: groupIndicators.map((id) => {
			const { label, values, valueLabel } = indicatorsIndex[id] as Indicator
			return {
				id,
				label,
				colors: values.map(({ color }) => color),
				categories: values.filter(({ color }) => color !== null).reverse(),
				valueLabel,
				layer: pixelLayerIndex[id]
			}
		})
	}

	renderLayerGroups.push(group)
	layers.push(...group.layers)
})

renderLayerGroups.push({
	id: 'otherInfo',
	label: 'More information',
	layers: otherInfoLayers
})

export const renderLayersIndex = indexBy(layers, 'id')
