import { SvelteSet } from 'svelte/reactivity'
import { browser } from '$app/environment'
import { replaceState } from '$app/navigation'
import { defaultFilters, filterToIndex } from '$lib/config/filters'
import { BLUEPRINT_VERSION } from '$lib/env'
import { logGAEvent } from '$lib/util/log'
import type { Filter, Filters } from '$lib/types'

type MapMode = 'unit' | 'pixel' | 'filter'
type FilterMode = 'AND' | 'OR'

export class MapData {
	#mapMode: MapMode = $state('unit')
	#data: any | null = $state.raw(null) // FIXME: typing
	#selectedIndicator: any | null = $state.raw(null) // FIXME: typing
	#filterMode: FilterMode = $state('AND')
	#filters: Filters = $state.raw(defaultFilters)
	#activeFilterValues = $derived(
		Object.fromEntries(
			Object.entries(this.#filters)
				.filter(([_, { enabled }]) => enabled)
				.map(([id, { activeValues }]) => [id, activeValues])
		)
	)
	#numEnabledFilters = $derived.by(
		() => Object.values(this.#filters).filter(({ enabled }) => enabled).length
	)
	#visibleSubregions: Set<string> = $state.raw(new SvelteSet<string>())
	#visibleRegions: Set<string> = $state.raw(new SvelteSet<string>())
	#filtersLoading: boolean = $state(true) // set to false on first set of visible subregions

	constructor() {
		this.restoreFromURL()
	}

	get mapMode(): string {
		return this.#mapMode
	}

	set mapMode(mode: MapMode) {
		this.#mapMode = mode
		this.#data = null
		this.#selectedIndicator = null
		this.saveToURL()
	}

	get data() {
		return this.#data
	}

	setData(data: any | null) {
		console.log('set map data', data)
		this.#data = data
		if (data === null) {
			this.#selectedIndicator = null
		} else if (data.type !== 'pixel') {
			logGAEvent('set-map-data', {
				type: data.type,
				id: `${data.type}:${data.id}`
			})
		}
	}

	get selectedIndicator() {
		return this.#selectedIndicator
	}

	set selectedIndicator(indicator) {
		this.#selectedIndicator = indicator

		if (indicator) {
			logGAEvent('show-indicator-details', {
				indicator
			})
		}
	}

	get filterMode() {
		return this.#filterMode
	}

	set filterMode(mode: FilterMode) {
		this.#filterMode = mode
		this.saveToURL()
	}

	get filters() {
		return this.#filters
	}

	get numEnabledFilters() {
		return this.#numEnabledFilters
	}

	get hasVisibleFilters() {
		return this.#visibleSubregions.size > 0 || this.numEnabledFilters > 0
	}

	setLayerFilterValues(id: string, { enabled, activeValues }: Filter) {
		this.#filters = {
			...this.#filters,
			[id]: { enabled, activeValues }
		}

		this.saveToURL()
	}

	get activeFilterValues() {
		return this.#activeFilterValues
	}

	resetFilters() {
		this.#filters = defaultFilters
		this.saveToURL()
	}

	get filtersLoading() {
		return this.#filtersLoading
	}

	get visibleSubregions() {
		return this.#visibleSubregions
	}

	set visibleSubregions(visibleSubregions: Set<string>) {
		this.#visibleSubregions = visibleSubregions
		this.#filtersLoading = false
	}

	get visibleRegions() {
		return this.#visibleRegions
	}

	set visibleRegions(visibleRegions: Set<string>) {
		this.#visibleRegions = visibleRegions
	}

	// for logging state
	toJSON() {
		return {
			mapMode: this.#mapMode,
			data: this.#data,
			selectedIndicator: this.#selectedIndicator,
			filters: this.#filters,
			visibleSubregions: this.#visibleSubregions,
			visibleRegions: this.#visibleRegions
		}
	}

	saveToURL() {
		if (browser) {
			const filterValues = Object.fromEntries(
				Object.entries(this.#activeFilterValues).map(([id, activeValues]) => [
					filterToIndex[id],
					Object.entries(activeValues)
						// eslint-disable-next-line @typescript-eslint/no-unused-vars
						.filter(([_, enabled]) => enabled)
						.map(([value]) => value)
						.join('.')
				])
			)
			if (Object.keys(filterValues).length > 0) {
				const urlState = {
					version: BLUEPRINT_VERSION,
					mode: this.#mapMode,
					filterMode: this.#filterMode,
					...filterValues
				}

				// eslint-disable-next-line svelte/prefer-svelte-reactivity
				const searchParams = new URLSearchParams([...Object.entries(urlState)])

				// eslint-disable-next-line svelte/no-navigation-without-resolve
				replaceState(`?${searchParams.toString()}` + window.location.hash, urlState)
			} else {
				// no filters, no need to persist other parts of state
				// NOTE: we have to include the leading ? or it doesn't clear out URL
				// eslint-disable-next-line svelte/no-navigation-without-resolve
				replaceState(`?${window.location.hash}`, {})
			}
		}
	}

	restoreFromURL() {
		if (browser) {
			if (browser && window.location.search) {
				// eslint-disable-next-line svelte/prefer-svelte-reactivity
				const queryParams = Object.fromEntries([...new URLSearchParams(window.location.search)])
				if (queryParams.version !== BLUEPRINT_VERSION) {
					alert(
						"Your URL includes filters based on a previous version of the Blueprint, which is not supported. We're clearing your filters and loading the latest Blueprint. Sorry about that!"
					)
					window.history.replaceState({}, '', `?${window.location.hash}`)
					return
				}
				if (queryParams.mode) {
					this.#mapMode = queryParams.mode as MapMode
				}
				if (queryParams.filterMode) {
					this.#filterMode = queryParams.filterMode as FilterMode
				}
				const initFilters = Object.fromEntries(
					Object.entries(defaultFilters).map(([id, { activeValues: defaultActiveValues }]) => {
						const index = filterToIndex[id]

						const activeValues =
							// eslint-disable-next-line svelte/prefer-svelte-reactivity
							queryParams[index] !== undefined ? new Set(queryParams[index]) : null

						return [
							id,
							{
								enabled: !!queryParams[index],
								activeValues: Object.fromEntries(
									Object.entries(defaultActiveValues).map(([v, defaultValueEnabled]) => [
										v,
										activeValues ? activeValues.has(v) : defaultValueEnabled
									])
								)
							}
						]
					})
				)
				this.#filters = initFilters
			}
		}
	}
}
