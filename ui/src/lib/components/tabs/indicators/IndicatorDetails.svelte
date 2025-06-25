<script lang="ts">
	import { getContext } from 'svelte'

	import ReplyIcon from '~icons/fa-solid/reply'
	import { Button } from '$lib/components/ui/button'
	import type { MapData } from '$lib/components/map'
	import { formatPercent } from '$lib/util/format'
	import { sum } from '$lib/util/data'
	import { cn } from '$lib/utils'

	import { NeedHelp } from '../general'
	import IndicatorPercentTable from './IndicatorPercentTable.svelte'

	const {
		type,
		label,
		ecosystem,
		description,
		url,
		goodThreshold,
		values,
		valueLabel,
		outsideSEPercent,
		icon
	} = $props()

	const mapData: MapData = getContext('map-data')

	const { totalIndicatorPercent, percentTableValues } = $derived.by(() => {
		const totalPercent = sum(values.map(({ percent }: { percent: number }) => percent))

		const tableValues = values
			.map((value: object, i: number) => ({
				...value,
				isHighValue: i === values.length - 1,
				isLowValue: i === 0
			}))
			.reverse()

		const notEvaluatedPercent = 100 - outsideSEPercent - totalPercent
		if (notEvaluatedPercent >= 1) {
			tableValues.push({
				value: -1,
				label: 'Not evaluated for this indicator',
				percent: notEvaluatedPercent
			})
		}

		if (outsideSEPercent >= 1) {
			tableValues.push({
				value: -3,
				label: 'Outside Southeast Blueprint',
				percent: outsideSEPercent
			})
		}

		return {
			percentTableValues: tableValues,
			totalIndicatorPercent: totalPercent
		}
	})
</script>

<div class="flex flex-col h-full overflow-hidden">
	<Button
		class="shadow-none rounded-none flex justify-between items-center py-4 md:py-2 pl-1 pr-4 border-b text-foreground text-wrap whitespace-break-spaces h-auto gap-4"
		style={`background-color:${ecosystem.color}; border-color:${ecosystem.borderColor};`}
		onclick={() => (mapData.selectedIndicator = null)}
	>
		<div class="flex items-start">
			<ReplyIcon class="size-3 flex-none text-grey-7" />
			<div class="flex gap-2 flex-auto items-center">
				<img
					src={icon}
					alt={`${ecosystem.label} icon`}
					class="flex-none size-10 bg-white rounded-full block"
				/>
				<div class="flex flex-col leading-tight items-start text-left">
					<div class="font-sm color-grey-8">
						{ecosystem.label}
					</div>
					<h4 class="text-xl leading-tight">
						{label}
					</h4>
				</div>
			</div>
		</div>
		{#if type !== 'pixel'}
			<div class="flex-none text-grey-8 text-sm text-right leading-tight">
				<b>{formatPercent(totalIndicatorPercent)}%</b>
				<br />
				of area
			</div>
		{/if}
	</Button>

	<div class="px-4 pb-4 h-full flex-auto overflow-y-auto">
		{#if valueLabel}
			<div class="mt-4 -mb-6 font-bold">{valueLabel}:</div>
		{/if}

		<IndicatorPercentTable values={percentTableValues} {goodThreshold} />

		<div
			class={cn('text-md leading-snug mt-2', {
				'mt-1': type === 'pixel'
			})}
		>
			{#if description.search(/<a/g) !== -1}
				TODO: dangerously set inner HTML
			{:else}
				{description}
			{/if}
		</div>

		<div class="mt-8">
			To learn more and explore the GIS data,{' '}
			<a href={url} target="_blank"> view this indicator in the SECAS Atlas </a>.
		</div>

		<NeedHelp />
	</div>
</div>
