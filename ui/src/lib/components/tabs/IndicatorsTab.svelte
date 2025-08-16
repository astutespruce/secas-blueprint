<script lang="ts">
	import { getContext } from 'svelte'

	import FreshwaterIcon from '$images/f.svg'
	import MarineIcon from '$images/m.svg'
	import TerrestrialIcon from '$images/t.svg'
	import { cn } from '$lib/utils'
	import type { MapData } from '$lib/components/map'
	import { Ecosystem, IndicatorDetails } from './indicators'

	const ecosystemIcons = {
		f: FreshwaterIcon,
		m: MarineIcon,
		t: TerrestrialIcon
	}

	const { type, indicators, outsideSEPercent, rasterizedAcres, class: className = '' } = $props()

	const mapData: MapData = getContext('map-data')
</script>

<section class={cn('flex-auto overflow-y-auto h-full', className)}>
	{#if mapData.selectedIndicator && !!indicators.indicators[mapData.selectedIndicator]}
		<IndicatorDetails
			{type}
			{...indicators.indicators[mapData.selectedIndicator]}
			{outsideSEPercent}
			{rasterizedAcres}
			icon={ecosystemIcons[indicators.indicators[mapData.selectedIndicator].ecosystem.id]}
		/>
	{:else}
		{#each indicators.ecosystems as ecosystem}
			<Ecosystem {type} {...ecosystem} icon={ecosystemIcons[ecosystem.id]} />
		{/each}
	{/if}
</section>
