import { indexBy } from '$lib/util/data'
import type { Indicator } from '$lib/types'

import rawBlueprint from '$constants/blueprint.json'
import rawCorridors from '$constants/corridors.json'
import ecosystems from '$constants/ecosystems.json'
import rawIndicators from '$constants/indicators.json'
import protectedAreas from '$constants/protected_areas.json'
import rawSLR from '$constants/slr.json'
import subregions from '$constants/subregions.json'
import urban from '$constants/urban.json'
import wildfireRisk from '$constants/wildfire_risk.json'

// import pixel layers
import pixelLayers0 from '$constants/pixel_layers_0.json'
import pixelLayers1 from '$constants/pixel_layers_1.json'
import pixelLayers2 from '$constants/pixel_layers_2.json'
import pixelLayers3 from '$constants/pixel_layers_3.json'
import pixelLayers4 from '$constants/pixel_layers_4.json'
import pixelLayers5 from '$constants/pixel_layers_5.json'
import pixelLayers6 from '$constants/pixel_layers_6.json'
import pixelLayers7 from '$constants/pixel_layers_7.json'
import pixelLayers8 from '$constants/pixel_layers_8.json'

// export unmodified values directly
export {
	ecosystems,
	protectedAreas,
	subregions,
	urban,
	wildfireRisk,
	pixelLayers0,
	pixelLayers1,
	pixelLayers2,
	pixelLayers3,
	pixelLayers4,
	pixelLayers5,
	pixelLayers6,
	pixelLayers7,
	pixelLayers8
}

export const ecosystemIndex = indexBy(ecosystems, 'id')

export const subregionsIndex = indexBy(subregions, 'subregion')

// Sort by descending value
export const blueprint = rawBlueprint.sort(({ value: leftValue }, { value: rightValue }) =>
	rightValue > leftValue ? 1 : -1
)
// skip the first value
export const blueprintCategories = blueprint.slice(0, blueprint.length - 1)

// put 0 value at end
export const corridors = rawCorridors.slice(1).concat(rawCorridors.slice(0, 1))

// select subset of fields and add position within list
export const indicators: Indicator[] = rawIndicators.map(
	(
		{
			id,
			label,
			url,
			description,
			goodThreshold,
			values,
			valueLabel,
			subregions: indicatorSubregions
		},
		i
	) => ({
		id,
		label,
		url,
		description,
		goodThreshold,
		values,
		valueLabel,
		subregions: new Set(indicatorSubregions),
		pos: i // position within list of indicators, used to unpack packed indicator values
	})
)

export const indicatorsIndex = indexBy(indicators, 'id')

// split depth and NODATA values
export const slrDepth = rawSLR.slice(0, 11)
export const slrNodata = rawSLR.slice(11)

export const subregionIndex = indexBy(subregions, 'value')
