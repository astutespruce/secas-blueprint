<script lang="ts">
	import { getContext } from 'svelte'

	import ExclamationTriangle from '~icons/fa-solid/exclamation-triangle'
	import FilterIcon from '~icons/fa-solid/filter'
	import TimesCircle from '~icons/fa-solid/times-circle'
	import { Button } from '$lib/components/ui/button'
	import BlueprintIcon from '$images/blueprint.svg'
	import FreshwaterIcon from '$images/f.svg'
	import MarineIcon from '$images/m.svg'
	import OtherInfoIcon from '$images/otherInfo.svg'
	import TerrestrialIcon from '$images/t.svg'
	import type { MapData } from '$lib/components/map'
	import { setIntersection } from '$lib/util/data'
	import type { Filter } from '$lib/types'
	import { cn } from '$lib/utils'
	import {
		priorityFilters as rawPriorityFilters,
		ecosystemFilters,
		otherInfoFilters as rawOtherInfoFilters
	} from '$lib/config/filters'
	import FilterGroup from '../filter/FilterGroup.svelte'

	const { class: className } = $props()
	const mapData: MapData = getContext('map-data')

	type FilterVisibilityStub = {
		canBeVisible: boolean
		enabled: boolean
	}

	let { priorityFilters, terrestrialFilters, freshwaterFilters, marineFilters, otherInfoFilters } =
		$derived.by(() => {
			return {
				priorityFilters: rawPriorityFilters
					.map((entry) => ({
						...entry,
						...mapData.filters[entry.id],
						canBeVisible: mapData.visibleSubregions.size > 0
					}))
					.filter(
						({ canBeVisible, enabled }: FilterVisibilityStub) => canBeVisible || enabled // mapData.filters[id].enabled
					),

				terrestrialFilters: ecosystemFilters.t.indicators
					.map(
						({
							id,
							subregions: indicatorSubregions,
							...rest
						}: {
							id: string
							subregions: Set<string>
						}) => ({
							id,
							...rest,
							...mapData.filters[id],
							canBeVisible: setIntersection(indicatorSubregions, mapData.visibleSubregions).size > 0
						})
					)
					.filter(
						({ canBeVisible, enabled }: FilterVisibilityStub) => canBeVisible || enabled // mapData.filters[id].enabled
					),

				freshwaterFilters: ecosystemFilters.f.indicators
					.map(
						({
							id,
							subregions: indicatorSubregions,
							...rest
						}: {
							id: string
							subregions: Set<string>
						}) => ({
							id,
							...rest,
							...mapData.filters[id],
							canBeVisible: setIntersection(indicatorSubregions, mapData.visibleSubregions).size > 0
						})
					)
					.filter(
						({ canBeVisible, enabled }: FilterVisibilityStub) => canBeVisible || enabled // mapData.filters[id].enabled
					),

				marineFilters: ecosystemFilters.m.indicators
					.map(
						({
							id,
							subregions: indicatorSubregions,
							...rest
						}: {
							id: string
							subregions: Set<string>
						}) => ({
							id,
							...rest,
							...mapData.filters[id],
							canBeVisible: setIntersection(indicatorSubregions, mapData.visibleSubregions).size > 0
						})
					)
					.filter(
						({ canBeVisible, enabled }: FilterVisibilityStub) => canBeVisible || enabled // mapData.filters[id].enabled
					),

				otherInfoFilters: rawOtherInfoFilters
					.map((entry) => ({
						...entry,
						...mapData.filters[entry.id],
						canBeVisible:
							(entry.id !== 'urban' &&
								entry.id !== 'wildfireRisk' &&
								mapData.visibleSubregions.size > 0) ||
							// urban / wildfire not in Caribbean
							((entry.id === 'urban' || entry.id === 'wildfireRisk') &&
								[...mapData.visibleSubregions].filter((s) => s !== 'Caribbean').length > 0)
					}))
					.filter(({ canBeVisible, enabled }: FilterVisibilityStub) => canBeVisible || enabled) // mapData.filters[id].enabled)
			}
		})

	const handleFilterChange = ({ id, enabled, activeValues }: Filter & { id: string }) => {
		mapData.setLayerFilterValues(id, { enabled, activeValues })
	}

	const handleResetFilters = () => {
		mapData.resetFilters()
	}
</script>

<section class={cn('flex flex-col h-full', className)}>
	<div class="flex justify-between flex-none pt-4 pb-2 px-2 border-b border-b-grey-3">
		<div class="flex items-center gap-2">
			<FilterIcon class="size-5" />
			<h3 class="text-2xl leading-tight">Filter the Blueprint</h3>
		</div>
		<div
			class={cn('flex justify-end items-center', {
				hidden: mapData.numEnabledFilters === 0
			})}
		>
			<Button onclick={handleResetFilters} class="text-sm px-2 gap-1 py-0 h-7">
				<TimesCircle width="1em" height="1em" class="p-0 m-0" />
				reset {mapData.numEnabledFilters} filter{mapData.numEnabledFilters > 1 ? 's' : ''}
			</Button>
		</div>
	</div>

	<div class="flex-auto h-full overflow-y-auto">
		{#if mapData.filtersLoading}
			<div class="mt-4 text-center text-xl text-grey-8">Loading...</div>
		{:else if mapData.hasVisibleFilters}
			<div class="flex flex-col overflow-y-auto flex-auto h-full relative">
				<div class="px-4 py-2 leading-tight text-grey-8">
					Filters can help you find the part of the Blueprint that aligns with your mission,
					interest, or specific question. Enable the filters below to narrow down the Blueprint to
					the part that falls within a range of values for one or more layers.
				</div>

				<FilterGroup
					id="priorities"
					label="Filter by priorities"
					icon={BlueprintIcon}
					color="bg-(--group-priorities)/5"
					borderColor="border-(--group-priorities)/20"
					entries={priorityFilters}
					onChange={handleFilterChange}
				/>

				<FilterGroup
					id="t"
					label="Filter by terrestrial indicators"
					icon={TerrestrialIcon}
					color="bg-(--group-terrestrial)/30"
					borderColor="border-(--group-terrestrial)"
					entries={terrestrialFilters}
					onChange={handleFilterChange}
				/>

				<FilterGroup
					id="f"
					label="Filter by freshwater indicators"
					icon={FreshwaterIcon}
					color="bg-(--group-freshwater)/20"
					borderColor="border-(--group-freshwater)"
					entries={freshwaterFilters}
					onChange={handleFilterChange}
				/>

				<FilterGroup
					id="m"
					label="Filter by coastal & marine indicators"
					icon={MarineIcon}
					color="bg-(--group-marine)/15"
					borderColor="border-(--group-marine)"
					entries={marineFilters}
					onChange={handleFilterChange}
				/>

				<FilterGroup
					id="otherInfo"
					label="More filters"
					icon={OtherInfoIcon}
					color="bg-(--group-other)/20"
					borderColor="border-(--group-other)/60"
					entries={otherInfoFilters}
					onChange={handleFilterChange}
				/>
			</div>
		{:else}
			<div class="py-8 pl-4 pr-8 flex justify-center">
				<div class="flex items-center gap-2">
					<ExclamationTriangle class="size-6 flex-none text-[orange]" />
					<div class="flex-auto text-grey-8 text-lg">No filters are available for this area.</div>
				</div>
			</div>
		{/if}
	</div>
</section>
