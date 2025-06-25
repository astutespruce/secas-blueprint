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
		'cursor-default shadow-none px-4 pt-4 pb-6 relative not-first:border-t-2 border-t-grey-1 group',
		{
			'cursor-pointer hover:bg-grey-0': !isZeroValue
		}
	)}
>
	<div
		class={cn('text-lg text-grey-8', {
			'text-primary font-bold': !isZeroValue
		})}
	></div>

	<IndicatorPixelValueChart {...indicator} {isPresent} {currentValue} {isZeroValue} />

	{#if !isZeroValue}
		<div
			class="text-primary font-sm text-center absolute bottom-0 top-0 left-0 right-0 hidden group-hover:block"
		>
			<div class="md:hidden">tap</div>
			<div class="hidden md:block">click</div>
			for more details
		</div>
	{/if}
</Button>
