<script lang="ts">
	import { getContext } from 'svelte'
	import ArrowUpIcon from '~icons/fa-solid/arrow-up'
	import ArrowDownIcon from '~icons/fa-solid/arrow-down'

	import { allFilters } from '$lib/config/filters'
	import type { MapData } from '$lib/components/map'

	const mapData: MapData = getContext('map-data')

	const activeFilters = $derived(
		allFilters
			.filter(({ id }) => mapData.activeFilterValues[id])
			.map(({ id, label, goodThreshold, values }) => {
				const activeValues = mapData.activeFilterValues[id]

				return {
					id,
					label,
					goodThreshold,
					values: values.map(({ value, label }) => ({
						value,
						label,
						enabled: activeValues[value]
					}))
				}
			})
	)
</script>

{#if activeFilters.length}
	<div class="flex gap-8 justify-between mt-8 break-before-page">
		<h2 class="text-xl">Active filters:</h2>
		<div class="text-sm text-muted-foreground flex gap-2">
			<div
				class="rounded-xs size-5 border border-black flex justify-center items-center leading-none"
			>
				X
			</div>
			indicates active filter value
		</div>
	</div>

	<div class="mt-1">
		Filter mode:.
		{#if mapData.filterMode === 'AND'}
			display only the areas where the selected filters overlap
		{:else}
			display all areas where any of the selected filters are present
		{/if}
		({mapData.filterMode} logic).
	</div>

	<div class="mt-4">
		{#each activeFilters as { id, label, goodThreshold, values } (id)}
			<div class="not-first:mt-6 break-inside-avoid">
				<div class="font-bold text-lg">{label}</div>
				<div>
					{#each values as { value, label: valueLabel, enabled } (value)}
						<div class="not-first:mt-1">
							{#if goodThreshold !== null && value + 1 === goodThreshold}
								<div class="mt-2 text-grey-8 text-xs">
									<div class="flex justify-center items-center gap-1">
										<ArrowUpIcon class="size-3" />
										<div class="w-[14em]">good condition</div>
									</div>
									<div class="border-b border-dashed border-b-grey-6 h-[1px] my-2"></div>
									<div class="flex justify-center items-center gap-1">
										<ArrowDownIcon class="size-3" />
										<div class="w-[14em]">not in good condition</div>
									</div>
								</div>
							{/if}
							<div class="flex gap-2">
								<div
									class="rounded-xs size-5 border border-black flex justify-center items-center leading-none"
								>
									{#if enabled}X{/if}
								</div>
								<div class="text-sm mt-0.25">
									{valueLabel}
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/each}
	</div>
{/if}
