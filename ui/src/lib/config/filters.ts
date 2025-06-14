import { indexBy, range, sortByFunc } from '$lib/util/data'
import type { Filters } from '$lib/types'
import {
	blueprint,
	corridors,
	ecosystems as rawEcosystems,
	indicators,
	indicatorsIndex,
	urban,
	slrDepth,
	slrNodata,
	wildfireRisk,
	protectedAreas
} from './constants'

// setup default filters
export const defaultFilters: Filters = Object.fromEntries(
	indicators.map(({ id, values }) => {
		const valuesIndex = indexBy(values, 'value')

		return [
			id,
			{
				enabled: false,
				activeValues: Object.fromEntries(
					range(values[0].value, values[values.length - 1].value + 1).map((v) => [
						v,
						// disable value if we don't normally show it
						valuesIndex[v] && valuesIndex[v].color !== null
					])
				)
			}
		]
	})
)

defaultFilters.blueprint = {
	enabled: false,
	// skip not a priority class; values 1-4
	activeValues: Object.fromEntries(range(1, 5).map((v) => [v, true]))
}

defaultFilters.corridors = {
	enabled: false,
	// values 1-6
	activeValues: Object.fromEntries(range(1, 7).map((v) => [v, true]))
}

defaultFilters.urban = {
	enabled: false,
	// values 1-5
	activeValues: Object.fromEntries(range(1, 6).map((v) => [v, true]))
}

defaultFilters.slr = {
	enabled: false,
	// hardcoded values to capture depth + nodata (values 0-13)
	activeValues: Object.fromEntries(range(0, 14).map((v) => [v, true]))
}

defaultFilters.wildfireRisk = {
	enabled: false,
	// values 0-10
	activeValues: Object.fromEntries(range(0, 11).map((v) => [v, true]))
}

defaultFilters.protectedAreas = {
	enabled: false,
	// values 0-1
	activeValues: { 0: false, 1: true }
}

export const priorityFilters = [
	{
		id: 'blueprint',
		label: 'Blueprint priority',
		description:
			'The Blueprint identifies priority areas based on a suite of natural and cultural resource indicators representing terrestrial, freshwater, and marine ecosystems.',
		values: blueprint.slice().sort(sortByFunc('value')).slice(1, blueprint.length).reverse()
	},
	{
		id: 'corridors',
		label: 'Hubs and corridors',
		values: corridors.filter(({ value }) => value > 0),
		description:
			'The Blueprint uses a least-cost path connectivity analysis to identify corridors that link hubs across the shortest distance possible, while also routing through as much Blueprint priority as possible.'
	}
]

export const ecosystemFilters = indexBy(
	rawEcosystems.map(({ indicators: ecosystemIndicators, ...ecosystem }) => ({
		...ecosystem,
		indicators: ecosystemIndicators.map((id) => ({
			...indicatorsIndex[id],
			// sort indicator values in descending order
			values: indicatorsIndex[id].values.slice().reverse()
		}))
	})),
	'id'
)

export const otherInfoFilters = [
	{
		id: 'urban',
		label: 'Probability of urbanization by 2060',
		values: urban
			.slice()
			// values are not in order and need to be sorted in ascending order
			.sort(sortByFunc('value')),
		description:
			'Past and current (2021) urban levels based on developed land cover classes from the National Land Cover Database. Future urban growth estimates derived from the FUTURES model developed by the Center for Geospatial Analytics, NC State University.  Data extent limited to the inland continental Southeast.'
	},
	{
		id: 'slr',
		label: 'Flooding extent by projected sea-level rise',
		values: slrDepth
			.map(({ label, ...rest }) => ({
				...rest,
				label: `${label} feet`
			}))
			.concat(slrNodata),
		description: 'Sea level rise estimates derived from the NOAA sea-level rise inundation data.'
	},
	{
		id: 'wildfireRisk',
		label: 'Wildfire likelihood (annual burn probability)',
		values: wildfireRisk,
		description:
			'Wildfire likelihood data derived from the Wildfire Risk to Communities project by the USDA Forest Service.'
	},
	{
		id: 'protectedAreas',
		label: 'Protected areas',
		values: protectedAreas,
		description:
			'Protected areas information is derived from the Protected Areas Database of the United States (PAD-US v4.0 and v3.0).'
	}
]
