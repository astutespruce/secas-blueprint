<script lang="ts">
	import { setContext } from 'svelte'
	import { defaultFilters } from '$lib/config/filters'
	import { renderLayersIndex } from '$lib/config/pixelLayers'
	import type { MapData } from '$lib/types'
	import { MobileTabs } from '$lib/components/layout'
	import { InfoTab, FiltersTab } from '$lib/components/tabs'
	import { Map } from '$lib/components/map'
	import { cn } from '$lib/utils'

	let mapData: MapData = $state({
		mapMode: 'unit', // filter, pixel, or unit
		isLoading: false,
		data: null,
		selectedIndicator: null,
		renderLayer: renderLayersIndex.blueprint,
		filters: defaultFilters,
		visibleSubregions: new Set()
	})
	setContext('map-data', mapData)

	// TODO: search state / context

	// TODO: may not need this, may be able to have every tab scroll itself instead
	let contentNode: Element | null = $state(null)

	// TODO: if mobile, tab is map, which really just means that map is on top
	// TODO: need responsive hook that if in map mode on mobile and made wider, sidebar reappears
	let tab = $state('info')
	const handleTabChange = (newTab: string) => {
		tab = newTab
		// scroll content to top
		if (contentNode) {
			contentNode.scrollTop = 0
		}
	}
</script>

<svelte:head>
	<title>Southeast Conservation Blueprint Explorer</title>
</svelte:head>

<div class="flex flex-col h-full flex-auto">
	<div class="flex h-full flex-auto overflow-y-hidden relative">
		<!-- sidebar -->
		<div
			bind:this={contentNode}
			class={cn(
				'md:block h-full bg-white grow shrink-0 basis-full md:basis-[360px] lg:basis-[468px] w-max-[100%] md:w-max-[360px] lg:w-max-[468px] flex-col overflow-hidden absolute md:relative left-0 right-0 top-0 bottom-0 z-[10000] md:z-[1] md:border-r-2 border-r-grey-3',
				{
					hidden: tab === 'map'
				}
			)}
		>
			{#if tab === 'info'}
				<InfoTab />
			{:else if tab === 'filter'}
				<FiltersTab />
			{:else}
				TODO: other tab content
			{/if}
		</div>

		<Map />
	</div>

	<!-- mobile bottom tabs	-->
	<MobileTabs
		{tab}
		hasMapData={mapData.data !== null && !mapData.isLoading}
		onChange={handleTabChange}
	/>
</div>
