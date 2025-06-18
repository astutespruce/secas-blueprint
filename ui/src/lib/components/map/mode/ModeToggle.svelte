<script lang="ts">
	import { logGAEvent } from '$lib/util/log'
	import { Button } from '$lib/components/ui/button'
	import ModeTooltip from './ModeTooltip.svelte'
	import { cn } from '$lib/utils'

	let { mapMode, belowMinZoom } = $props()

	const handleFilterClick = () => {
		mapMode = 'filter'
		logGAEvent('set-map-mode', { mode: 'filter' })
	}

	const handlePixelClick = () => {
		mapMode = 'pixel'
		logGAEvent('set-map-mode', { mode: 'pixel-identify' })
	}

	const handleUnitClick = () => {
		mapMode = 'unit'
		logGAEvent('set-map-mode', { mode: 'summary-unit' })
	}

	const inactiveClass = {
		'bg-blue-2': true
	}

	const activeClass = {
		'bg-primary': true,
		'text-white': true
	}
</script>

<div
	class="flex flex-col md:flex-wrap md:flex-row justify-center md:justify-start md:gap-2 absolute text-center pt-3 pb-2 px-4 bg-white text-grey-8 shadow-md shadow-grey-6 font-sm md:font-md z-[1000] left-0 md:left-[21px] right-0 md:right-auto bottom-0 md:bottom-auto md:top-0 md:rounded-b-xl"
>
	<div class="flex items-center flex-nowrap justify-center md:justify-start gap-[1px]">
		<ModeTooltip
			content="Show data summaries and charts for a subwatershed or marine hexagon"
			onClick={handleUnitClick}
			class={cn(mapMode === 'unit' ? activeClass : inactiveClass)}
		>
			Summarize data
		</ModeTooltip>

		<ModeTooltip
			content="Show values at a specific point for the Blueprint, indicators, and other contextual information"
			onClick={handlePixelClick}
			class={cn(mapMode === 'pixel' ? activeClass : inactiveClass)}
		>
			View point data
		</ModeTooltip>

		<ModeTooltip
			content="Find your part of the Blueprint by showing only areas that score within a certain range on indicators and more"
			onClick={handleFilterClick}
			class={cn('', mapMode === 'filter' ? activeClass : inactiveClass)}
		>
			Filter the Blueprint
		</ModeTooltip>
	</div>
	<div class="text-xs md:text-sm text-center md:text-left ml-2 leading-none mt-1 md:mt-0">
		{#if (mapMode === 'unit' || mapMode === 'pixel') && belowMinZoom}
			<div class="md:max-w-[6em]">
				Zoom in to select {mapMode === 'pixel' ? 'a point' : 'an area'}
			</div>
		{:else if mapMode === 'unit'}
			<div class="md:max-w-[16em]">
				Select a subwatershed or marine hexagon to show details
				<span class="hidden md:inline">in sidebar</span>
			</div>
		{:else if mapMode === 'pixel'}
			<div class="md:max-w-[16em]">
				Pan the map behind the crosshairs to show details
				<span class="hidden md:inline"> in sidebar</span>
			</div>
		{:else if mapMode === 'filter'}
			<div class="md:max-w-[18em]">
				Select one or more indicators to filter and adjust the range to update the map
			</div>
		{/if}
	</div>
</div>
