<script lang="ts">
	import { getContext } from 'svelte'

	import { cn } from '$lib/utils'
	import type { MapData } from '$lib/components/map'
	import { Button } from '$lib/components/ui/button'

	import IndicatorPixelValueChart from './IndicatorPixelValueChart.svelte'

	const { indicator, onSelect } = $props()

	const mapData: MapData = getContext('map-data')

	let { isPresent, isZeroValue, currentValue } = $derived.by(() => {
		const present = indicator.total > 0
		const [value] = indicator.values.filter(({ percent }: { percent: number }) => percent === 100)
		const zeroVaue: boolean = !present || (value.value === 0 && !value.color)

		return {
			isPresent: present,
			currentValue: value,
			isZeroValue: zeroVaue
		}
	})
</script>

<Button
	onclick={!isZeroValue
		? () => {
				mapData.selectedIndicator = indicator.id
			}
		: () => {}}
	class={cn(
		'block text-left cursor-default bg-white hover:bg-white w-full shadow-none rounded-none px-4 pt-4 pb-6 relative not-first:border-t-2 border-t-grey-1 h-auto group',
		{
			'cursor-pointer hover:bg-grey-0': !isZeroValue
		}
	)}
>
	<div
		class={cn('text-lg text-grey-8', {
			'text-primary font-bold': !isZeroValue
		})}
	>
		{indicator.label}
	</div>

	<IndicatorPixelValueChart {...indicator} {isPresent} {currentValue} {isZeroValue} />

	{#if !isZeroValue}
		<div
			class="text-primary leading-none font-sm text-center absolute bottom-1 left-0 right-0 hidden group-hover:block"
		>
			<span class="md:hidden">tap</span>
			<span class="hidden md:inline">click</span>
			for more details
		</div>
	{/if}
</Button>
