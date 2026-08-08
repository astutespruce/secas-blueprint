import { indexBy } from '$lib/util/data'
import type {
	Indicator,
	PixelLayerBounds,
	PixelLayerEncodings,
	PixelLayerIndex,
	PixelLayer
} from '$lib/types'

import {
	blueprint,
	corridors,
	indicatorGroups,
	indicatorsIndex,
	parcas,
	protectedAreas,
	urban,
	slrDepth,
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
		id: blueprint.id,
		label: 'Blueprint priority',
		valueLabel: 'for a connected network of lands and waters', // used in legend
		colors: blueprint.values.map(({ color, value }) => (value === 0 ? null : color)),
		categories: blueprint.values.filter(({ value }) => value > 0),
		layer: pixelLayerIndex[blueprint.id]
	},
	{
		id: corridors.id,
		label: 'Hubs and corridors',
		colors: corridors.values.map(({ color }) => color),
		categories: corridors.values
			.filter(({ value }) => value > 0)
			.map(({ value, label, color }) => ({
				value,
				label,
				color
			})),
		layer: pixelLayerIndex[corridors.id]
	}
]

const otherInfoLayers: PixelLayer[] = [
	{
		id: slrDepth.id,
		label: slrDepth.label,
		colors: slrDepth.values.map(({ color }) => color),
		categories: slrDepth.values
			.filter(({ value }) => value !== 13)
			.map(({ label, ...rest }) => ({
				...rest,
				label,
				outlineWidth: 1,
				outlineColor: 'grey.5'
			})),
		layer: pixelLayerIndex[slrDepth.id]
	},
	{
		id: parcas.id,
		label: parcas.label,
		colors: parcas.values.map(({ color }) => color),
		categories: parcas.values.filter(({ color }) => color !== null),
		layer: pixelLayerIndex[parcas.id]
	},
	{
		id: urban.id,
		label: urban.label,
		colors: urban.values.map(({ color }) => color),
		categories: urban.values.map(({ color, ...rest }) => ({
			...rest,
			color: color || '#FFFFFF',
			outlineWidth: 1,
			outlineColor: 'grey.5'
		})),
		layer: pixelLayerIndex[urban.id]
	},
	{
		id: protectedAreas.id,
		label: protectedAreas.label,
		colors: protectedAreas.values.map(({ color }) => color),
		categories: protectedAreas.values.filter(({ color }) => color !== null),
		layer: pixelLayerIndex[protectedAreas.id]
	},
	{
		id: wildfireRisk.id,
		label: wildfireRisk.label,
		colors: wildfireRisk.values.map(({ color }) => color),
		// sort in descending order
		// NOTE: this uses a custom legend for simple label values, not the full
		// set of categories
		categories: Object.values(
			Object.fromEntries(
				wildfireRisk.values
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
		layer: pixelLayerIndex[wildfireRisk.id]
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

indicatorGroups.forEach(({ id: groupId, label: groupLabel, indicators: groupIndicators }) => {
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

export const paletteSize =
	Math.max(
		// @ts-expect-error colors is valid
		...(Object.values(renderLayersIndex).map(({ colors }) => colors.length) as number[])
	) + 1
