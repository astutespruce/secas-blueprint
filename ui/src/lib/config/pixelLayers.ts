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
	parcas,
	protectedAreas,
	urban,
	slrDepth,
	slrNodata,
	wildfireRisk,
	pixelLayers0,
	pixelLayers1,
	pixelLayers2,
	pixelLayers3,
	pixelLayers4,
	pixelLayers5,
	pixelLayers6,
	pixelLayers7,
	pixelLayers8,
	pixelLayers9
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
	8: pixelLayers8,
	9: pixelLayers9
}

// this is copy-pasted from bounds reported by the tile services
const pixelLayerBounds: PixelLayerBounds = {
	0: [-108.0227, 16.97285, -57.03082, 41.58111],
	1: [-108.0227, 23.7876, -74.16891, 41.58053],
	2: [-108.0227, 23.78657, -74.16925, 41.58053],
	3: [-108.0227, 23.73322, -74.0301, 41.58035],
	4: [-98.17642, 23.45445, -78.08619, 37.43742],
	5: [-98.52635, 22.4353, -70.45003, 40.4673],
	6: [-98.36691, 22.37943, -70.45039, 40.46605],
	7: [-67.97848, 16.97285, -64.29697, 19.34715],
	8: [-67.97848, 16.97285, -64.29697, 19.34715],
	9: [-98.77728, 16.97285, -57.624, 40.36192]
}

const pixelLayerSourceConfig = { tileSize: 512, minzoom: 3, maxzoom: 14 }

export const pixelLayers = [...Array(10).keys()].map((i) => ({
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
	},
	{
		id: 'parcas',
		label: 'Priority Amphibian and Reptile Conservation Areas',
		colors: parcas.map(({ color }) => color),
		categories: parcas.filter(({ color }) => color !== null),
		layer: pixelLayerIndex.parcas
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
