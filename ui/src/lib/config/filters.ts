import { indexBy, range } from '$lib/util/data'
import type { Filters } from '$lib/types'
import { indicators } from './constants'

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
