<script lang="ts">
	import { getContext } from 'svelte'

	import FreshwaterIcon from '$images/f.svg'
	import MarineIcon from '$images/m.svg'
	import TerrestrialIcon from '$images/t.svg'
	import { cn } from '$lib/utils'
	import type { MapState } from '$lib/components/map'
	import { IndicatorGroup, IndicatorDetails } from './indicators'

	const indicatorGroupIcons = {
		f: FreshwaterIcon,
		m: MarineIcon,
		t: TerrestrialIcon
	}

	const {
		type,
		indicators,
		outside_extent_percent,
		rasterized_acres,
		class: className = ''
	} = $props()

	const mapState: MapState = getContext('map-state')
</script>

<section class={cn('flex-auto overflow-y-auto h-full', className)}>
	{#if mapState.selectedIndicator && !!indicators.indicators[mapState.selectedIndicator]}
		<IndicatorDetails
			{type}
			{...indicators.indicators[mapState.selectedIndicator]}
			{outside_extent_percent}
			{rasterized_acres}
			icon={indicatorGroupIcons[
				indicators.indicators[mapState.selectedIndicator].group
					.id as keyof typeof indicatorGroupIcons
			]}
		/>
	{:else}
		{#each indicators.indicatorGroups as group (group.id)}
			<IndicatorGroup
				{type}
				{...group}
				icon={indicatorGroupIcons[group.id as keyof typeof indicatorGroupIcons]}
			/>
		{/each}
	{/if}
</section>
