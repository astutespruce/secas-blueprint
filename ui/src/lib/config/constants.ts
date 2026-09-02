import { indexBy } from '$lib/util/data'
import type { Indicator } from '$lib/types'

import blueprint from '$constants/blueprint.json'
import corridors from '$constants/corridors.json'
import indicatorGroups from '$constants/indicator_groups.json'
import rawIndicators from '$constants/indicators.json'
import parcas from '$constants/parcas.json'
import parcasPoly from '$constants/parcas_poly.json'
import protectedAreas from '$constants/protected_areas.json'
import protectedAreasPoly from '$constants/protected_areas_poly.json'
import slrDepth from '$constants/slr_depth.json'
import slrProj from '$constants/slr_proj.json'
import subregions from '$constants/subregions.json'
import urban from '$constants/urban.json'
import urbanByDecade from '$constants/urban_by_decade.json'
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
import pixelLayers9 from '$constants/pixel_layers_9.json'

// export unmodified values directly
export {
	blueprint,
	corridors,
	indicatorGroups,
	parcas,
	parcasPoly,
	protectedAreas,
	protectedAreasPoly,
	slrDepth,
	slrProj,
	subregions,
	urban,
	urbanByDecade,
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
}

export const indicatorGroupIndex = indexBy(indicatorGroups, 'id')

export const subregionsIndex = indexBy(subregions, 'subregion')

// select subset of fields and add position within list
// use the order as defined in the indicator groups
const indicatorIds: string[] = []
indicatorGroups.forEach(({ indicators: groupIndicators }) => {
	indicatorIds.push(...groupIndicators)
})
const rawIndicatorsIndex = Object.fromEntries(
	rawIndicators.map((indicator) => [indicator.id, indicator])
)

export const indicators: Indicator[] = indicatorIds.map((id, i) => {
	const indicator = rawIndicatorsIndex[id]
	return {
		...indicator,
		subregions: new Set(indicator.subregions),
		pos: i
	}
})

export const indicatorsIndex = indexBy(indicators, 'id')

export const subregionIndex = indexBy(subregions, 'value')
