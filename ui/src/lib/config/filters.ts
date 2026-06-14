import { indexBy, range } from '$lib/util/data'
import type { Filters } from '$lib/types'
import {
	blueprint,
	corridors,
	ecosystems as rawEcosystems,
	indicators,
	indicatorsIndex,
	urban,
	slrDepth,
	wildfireRisk,
	protectedAreas,
	parcas
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

defaultFilters.parcas = {
	enabled: false,
	// values 0-1
	activeValues: { 0: false, 1: true }
}

defaultFilters.protectedAreas = {
	enabled: false,
	// values 0-1
	activeValues: { 0: false, 1: true }
}

export const priorityFilters = [
	{
		id: blueprint.id,
		label: blueprint.label,
		description: blueprint.description,
		values: blueprint.values.filter(({ value }) => value > 0).reverse()
	},
	{
		id: corridors.id,
		label: corridors.label,
		values: corridors.values.filter(({ value }) => value > 0),
		description: corridors.description
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
		id: slrDepth.id,
		label: slrDepth.label,
		values: slrDepth.values.map(({ value, label, ...rest }) => ({
			...rest,
			value,
			label: value < 11 ? `${label} feet` : label
		})),
		description: slrDepth.description
	},
	{
		id: parcas.id,
		label: parcas.label,
		values: parcas.values,
		description: parcas.description
	},
	{
		id: urban.id,
		label: urban.label,
		values: urban.values,
		description: urban.description
	},
	{
		id: protectedAreas.id,
		label: protectedAreas.label,
		values: protectedAreas.values,
		description: protectedAreas.description
	},
	{
		id: wildfireRisk.id,
		label: wildfireRisk.label,
		values: wildfireRisk.values,
		description: wildfireRisk.description
	}
]
