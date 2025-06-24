<script lang="ts">
	import { setContext, untrack } from 'svelte'
	import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query'

	import type { LocationData } from '$lib/types'
	import {
		Footer,
		Header,
		MobileDetailsHeader,
		MobileTabs,
		SidebarDetailsHeader
	} from '$lib/components/layout'
	import { Map, MapData } from '$lib/components/map'
	import {
		ContactTab,
		FiltersTab,
		FindLocationTab,
		IndicatorsTab,
		InfoTab,
		MoreInfoTab,
		PrioritiesTab
	} from '$lib/components/tabs'
	import { cn } from '$lib/utils'

	let isMobile: boolean = $state(false)

	const mapData = new MapData()
	setContext('map-data', mapData)
	$inspect('mapData', mapData)

	let locationData: LocationData = $state({ location: null })
	setContext('location-data', locationData)

	// TODO: may not need this, may be able to have every tab scroll itself instead
	let contentNode: Element | null = $state(null)

	// default tabs: info, filter, map (mobile), find (mobile), contact (mobile)
	// data tabs: map (mobile), selected-priorities, selected-indicators, selected-more-info
	let tab = $state('info') // will be set to map if detected on mobile in attachment below
	let prevMobileTab: string | null = $state(null)

	$effect(() => {
		tab
		isMobile
		mapData.mapMode
		mapData.data

		// on mobile, no need to change tabs based on selection / deselection of data
		// or changing map mode
		if (isMobile) {
			if (mapData.data === null && tab.startsWith('selected-')) {
				tab = 'map'
			}
		} else {
			if (mapData.data === null && tab.startsWith('selected-')) {
				tab = 'info'
			} else if (mapData.mapMode === 'filter' && tab !== 'filter') {
				tab = 'filter'
			} else if (tab === 'filter' && mapData.mapMode !== 'filter') {
				tab = mapData.data !== null ? 'selected-priorities' : 'info'
			} else if (tab === 'info' && mapData.data !== null) {
				tab = 'selected-priorities'
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

	const handleWindowMatchMediaChange = ({ matches: nextIsMobile }: { matches: boolean }) => {
		let nextTab = tab

		if (isMobile && !nextIsMobile) {
			prevMobileTab = tab

			// switched from mobile to desktop; if on any of the mobile-only tabs, switch to info
			if (tab === 'map' || tab === 'find' || tab === 'contact') {
				// reset to info tab (default) on desktop
				nextTab = 'info'
			}
		} else if (!isMobile && nextIsMobile) {
			// switched from desktop to mobile
			if (tab === 'info') {
				// reset to map tab (default) on mobile
				nextTab = prevMobileTab || 'map'
			}
		}

		isMobile = nextIsMobile
		tab = nextTab
	}

	const windowMediaQueryHandler = (w: Window) => {
		// match tailwind "md" breakpoint
		const mediaQueryList = w.matchMedia('(max-width:768px)')

		// set mobile default tab on init
		if (mediaQueryList.matches && untrack(() => tab) === 'info') {
			tab = 'map'
		}

		isMobile = mediaQueryList.matches
		mediaQueryList.addEventListener('change', handleWindowMatchMediaChange)

		return () => {
			mediaQueryList.removeEventListener('change', handleWindowMatchMediaChange)
		}
	}
</script>

<svelte:head>
	<title>Southeast Conservation Blueprint Explorer</title>
</svelte:head>

<svelte:window {@attach windowMediaQueryHandler} />

<QueryClientProvider client={new QueryClient()}>
	<Header hasData={mapData && mapData.data !== null} />
	{#if isMobile && mapData && mapData.data}
		<MobileDetailsHeader {...mapData.data} onClose={() => mapData.setData(null)} />
	{/if}

	<div class="h-full w-full flex-auto overflow-auto">
		<div class="flex flex-col h-full flex-auto">
			<div class="flex h-full flex-auto overflow-y-hidden relative">
				<!-- sidebar -->
				<div
					bind:this={contentNode}
					class={cn(
						'md:flex h-full bg-white grow shrink-0 basis-full md:basis-[360px] lg:basis-[468px] w-max-[100%] md:w-max-[360px] lg:w-max-[468px] flex-col overflow-hidden absolute md:relative left-0 right-0 top-0 bottom-0 z-[10000] md:z-[1] md:border-r-2 border-r-grey-3',
						{
							hidden: tab === 'map'
						}
					)}
				>
					{#if !isMobile && mapData.data !== null}
						<SidebarDetailsHeader {tab} onTabChange={handleTabChange} />
					{/if}

					<InfoTab class={tab === 'info' ? '' : 'hidden'} />
					<FiltersTab class={tab === 'filter' ? '' : 'hidden'} />
					<FindLocationTab
						onSetLocation={handleSetLocation}
						class={tab === 'find' ? '' : 'hidden'}
					/>
					<ContactTab class={tab === 'contact' ? '' : 'hidden'} />

					<!-- selected data tabs -->
					<!-- type={mapData.data.type}
							blueprint={mapData.data.blueprint}
							corridors={mapData.data.corridors}
							subregions={mapData.data.subregions}
							outsideSEPercent={mapData.data.outsideSEPercent} -->
					{#if mapData.data !== null}
						<PrioritiesTab
							class={tab === 'selected-priorities' ? '' : 'hidden'}
							{...mapData.data}
						/>
						<IndicatorsTab class={tab === 'selected-indicators' ? '' : 'hidden'} />
						<MoreInfoTab class={tab === 'selected-more-info' ? '' : 'hidden'} />
					{/if}
				</div>

				<Map />
			</div>

			<!-- mobile bottom tabs	-->
			<MobileTabs {tab} onChange={handleTabChange} />
		</div>
	</div>
	<Footer />
</QueryClientProvider>
