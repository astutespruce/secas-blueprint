<script lang="ts">
	import { setContext } from 'svelte'
	import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query'

	import { defaultFilters } from '$lib/config/filters'
	import { renderLayersIndex } from '$lib/config/pixelLayers'
	import type { LocationData } from '$lib/types'
	import { MobileTabs } from '$lib/components/layout'
	import { Map, MapData } from '$lib/components/map'
	import { ContactTab, FiltersTab, FindLocationTab, InfoTab } from '$lib/components/tabs'
	import { cn } from '$lib/utils'

	let innerWidth: number | null = $state(null)

	const mapData = new MapData()
	setContext('map-data', mapData)
	$inspect('mapData', mapData)

	let locationData: LocationData = $state({ location: null })
	setContext('location-data', locationData)

	// TODO: may not need this, may be able to have every tab scroll itself instead
	let contentNode: Element | null = $state(null)

	// default tabs: info, filter, map (mobile), find (mobile), contact (mobile)
	// data tabs: mobile-selected-map (mobile), selected-priorities, selected-indicators, selected-more-info
	let tab = $state('info')

	$effect(() => {
		if (innerWidth === null) {
			return
		}

		const isMobile = innerWidth <= 768
		if (!isMobile) {
			if (tab === 'map' || tab === 'find' || tab === 'contact') {
				// reset to info tab on desktop
				tab = 'info'
			}
			// TODO: mobile-selected-map
			else if (mapData.mapMode === 'filter' && tab !== 'filter') {
				tab = 'filter'
			} else if (tab === 'filter' && mapData.mapMode !== 'filter') {
				// FIXME: based on data present
				tab = 'info'
			}
		}
	})

	const handleSetLocation = () => {
		if (tab === 'find' && !!locationData.location) {
			tab = 'map'
		}
	}

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

<svelte:window bind:innerWidth />

<QueryClientProvider client={new QueryClient()}>
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
				<InfoTab class={tab === 'info' ? '' : 'hidden'} />
				<FiltersTab class={tab === 'filter' ? '' : 'hidden'} />
				<FindLocationTab onSetLocation={handleSetLocation} class={tab === 'find' ? '' : 'hidden'} />
				<ContactTab class={tab === 'contact' ? '' : 'hidden'} />

				<!-- TODO: other tab content -->
			</div>

			<Map />
		</div>

		<!-- mobile bottom tabs	-->
		<MobileTabs {tab} onChange={handleTabChange} />
	</div>
</QueryClientProvider>
