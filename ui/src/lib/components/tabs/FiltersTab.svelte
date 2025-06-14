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
	import { defaultFilters } from '$lib/config/filters'
	import { setIntersection } from '$lib/util/data'
	import type { Filter, MapData } from '$lib/types'
	import { cn } from '$lib/utils'
	import { priorityFilters, ecosystemFilters, otherInfoFilters } from '$lib/config/filters'
	import FilterGroup from '../filter/FilterGroup.svelte'

	const mapData: MapData = getContext('map-data')

	const numFilters = $derived(
		Object.values(mapData.filters).filter(({ enabled }) => enabled).length
	)
	const hasVisibleFilters = $derived(mapData.visibleSubregions.size > 0 || numFilters > 0)

	const handleFilterChange = ({ id, enabled, activeValues }: Filter & { id: string }) => {
		mapData.filters = {
			...mapData.filters,
			[id]: {
				enabled,
				activeValues
			}
		}
	}

	const handleResetFilters = () => {
		mapData.filters = defaultFilters
	}
</script>

<div class="flex justify-between flex-none pt-4 pb-2 px-2 border-b border-b-grey-3">
	<div class="flex items-center gap-2">
		<FilterIcon class="size-5" />
		<h3 class="text-2xl leading-tight">Filter the Blueprint</h3>
	</div>
	<div
		class={cn('flex justify-end items-center', {
			hidden: numFilters === 0
		})}
	>
		<Button onclick={handleResetFilters} class="text-sm px-2 gap-1 py-0 h-7">
			<TimesCircle width="1em" height="1em" class="p-0 m-0" />
			reset {numFilters} filter{numFilters > 1 ? 's' : ''}
		</Button>
	</div>
</div>

<div class="h-full overflow-y-auto">
	{#if hasVisibleFilters}
		<div class="flex flex-col overflow-y-auto flex-auto h-full relative">
			<div class="px-4 py-2 leading-tight text-grey-8">
				Filters can help you find the part of the Blueprint that aligns with your mission, interest,
				or specific question. Enable the filters below to narrow down the Blueprint to the part that
				falls within a range of values for one or more layers.
			</div>

			<FilterGroup
				id="blueprint"
				label="Filter by priorities"
				icon={BlueprintIcon}
				color="bg-(--group-priorities)/5"
				borderColor="border-(--group-priorities)/20"
				entries={priorityFilters.map((entry) => ({
					...entry,
					canBeVisible: mapData.visibleSubregions.size > 0
				}))}
				filters={mapData.filters}
				onChange={handleFilterChange}
			/>

			<FilterGroup
				id="t"
				label="Filter by terrestrial indicators"
				icon={TerrestrialIcon}
				color="bg-(--group-terrestrial)/30"
				borderColor="border-(--group-terrestrial)"
				entries={ecosystemFilters.t.indicators.map(
					({ subregions: indicatorSubregions, ...rest }) => ({
						...rest,
						canBeVisible: setIntersection(indicatorSubregions, mapData.visibleSubregions).size > 0
					})
				)}
				filters={mapData.filters}
				onChange={handleFilterChange}
			/>

			<FilterGroup
				id="f"
				label="Filter by freshwater indicators"
				icon={FreshwaterIcon}
				color="bg-(--group-freshwater)/20"
				borderColor="border-(--group-freshwater)"
				entries={ecosystemFilters.f.indicators.map(
					({ subregions: indicatorSubregions, ...rest }) => ({
						...rest,
						canBeVisible: setIntersection(indicatorSubregions, mapData.visibleSubregions).size > 0
					})
				)}
				filters={mapData.filters}
				onChange={handleFilterChange}
			/>

			<FilterGroup
				id="m"
				label="Filter by coastal & marine indicators"
				icon={MarineIcon}
				color="bg-(--group-marine)/15"
				borderColor="border-(--group-marine)"
				entries={ecosystemFilters.m.indicators.map(
					({ subregions: indicatorSubregions, ...rest }) => ({
						...rest,
						canBeVisible: setIntersection(indicatorSubregions, mapData.visibleSubregions).size > 0
					})
				)}
				filters={mapData.filters}
				onChange={handleFilterChange}
			/>

			<FilterGroup
				id="otherInfo"
				label="More filters"
				icon={BlueprintIcon}
				color="bg-(--group-other)/20"
				borderColor="border-(--group-other)/60"
				entries={otherInfoFilters.map((entry) => ({
					...entry,
					canBeVisible: mapData.visibleSubregions.size > 0
				}))}
				filters={mapData.filters}
				onChange={handleFilterChange}
			/>
		</div>
	{:else}
		<div class="py-8 pl-4 pr-8 flex items-center gap-4">
			<ExclamationTriangle width="2em" height="2em" class="flex-none text-[orange]" />
			<div class="flex-auto text-grey-8 font-bold">No filters are available for this area.</div>
		</div>
	{/if}
</div>
