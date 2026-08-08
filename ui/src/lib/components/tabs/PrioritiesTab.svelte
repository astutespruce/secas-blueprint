<script lang="ts">
	import CheckIcon from '~icons/fa-solid/check'
	import { blueprint as blueprintInfo, corridors as corridorInfo } from '$lib/config/constants'
	import { PieChart } from '$lib/components/chart'
	import { cn } from '$lib/utils'
	import { NeedHelp } from './general'

	type Props = {
		type: string
		blueprint: number[] | number | null
		corridors: number[] | number | null
		regions: Set<string>
		outside_se_percent: number
		class: string | undefined
	}

	const {
		type,
		blueprint,
		corridors,
		regions,
		outside_se_percent,
		class: className = ''
	}: Props = $props()

	type Category = {
		value: number
		label: string
		color: string
	}

	const blueprintPixelValue = $derived(type === 'pixel' ? blueprint : null)
	const blueprintChartData = $derived.by(() => {
		if (type === 'pixel') {
			return null
		}

		if (blueprint === null) {
			return []
		}

		const blueprintPercents = (blueprint as number[]).slice().reverse()
		const data: Category[] = blueprintInfo.values
			.slice()
			.reverse()
			.map(({ color, ...rest }, i) => ({
				...rest,
				// add transparency to match map
				color: `${color}bf`,
				value: blueprintPercents[i]
			}))
			.filter(({ value }) => value > 0)

		if (outside_se_percent) {
			data.push({
				value: outside_se_percent,
				color: '#fde0dd',
				label: 'Outside Southeast Blueprint'
			})
		}
		return data
	})

	// given a summary unit or pixel, there will only ever be continental
	// or caribben corridors possible
	const availableCorridorCategories = $derived(
		corridorInfo.values
			.filter(({ value }) => value > 0 || type === 'pixel')
			.map(({ value, description, ...rest }) => {
				if (value === 1 && description) {
					const parts = description.split('  ')
					return {
						...rest,
						value,
						description: regions && regions.has('caribbean') ? parts[1] : parts[0]
					}
				}

				return { ...rest, value, description }
			})
	)

	const corridorChartData = $derived.by(() => {
		if (type === 'pixel') {
			return null
		}

		if (corridors === null) {
			return []
		}

		// sort categories into ascending order
		const data: Category[] = corridorInfo.values
			.map(({ value, color, ...rest }, i) => ({
				...rest,
				color: value === 0 ? '#ffebc2' : color,
				value: (corridors as number[])[i]
			}))
			.filter(({ value }) => value > 0)

		if (outside_se_percent) {
			data.push({
				value: outside_se_percent,
				color: '#fde0dd',
				label: 'Outside Southeast Blueprint'
			})
		}
		return data
	})
</script>

<section class={cn('flex-auto overflow-y-auto h-full p-4', className)}>
	<h3 class="text-2xl">Southeast Blueprint 2025 Priority</h3>
	<div class="text-grey-9">for a connected network of lands and waters</div>
	{#if type !== 'pixel'}
		<PieChart categories={blueprintChartData} class="mt-6 mb-4" />
	{/if}

	{#if outside_se_percent < 100}
		<div class="mt-2">
			{#each blueprintInfo.values
				.slice()
				.reverse() as { value, label, percent, color, description } (value)}
				<div
					class={cn(
						'flex justify-between items-start gap-2 text-grey-8 border border-transparent py-2 px-4 rounded-[0.5rem] bg-white not-first:mt-2',
						{
							'border-grey-2 shadow-md text-foregrund': value === blueprintPixelValue
						}
					)}
				>
					<div
						class="border border-grey-2 w-4 h-8 rounded-[0.25em] flex-none"
						style={`background-color:${color}bf;`}
					></div>
					<div class="flex-auto">
						<div class="font-bold">{label}</div>
						<div class="text-sm leading-snug">
							{description} This class covers {percent}% of the Southeast Blueprint geography.
						</div>
					</div>
					{#if value === blueprintPixelValue}
						<CheckIcon class="flex-none size-4" />
					{/if}
				</div>
			{/each}
		</div>
	{/if}

	<hr />

	<h3 class="text-2xl">Hubs and Corridors</h3>

	{#if type !== 'pixel'}
		<PieChart categories={corridorChartData} class="mt-6 mb-4" radius={28} lineWidth={25} />
	{/if}

	{#if outside_se_percent < 100}
		<div class="mt-2">
			{#each availableCorridorCategories as { value, label, description } (value)}
				<div
					class={cn(
						'flex justify-between items-start gap-2 text-grey-8 border border-transparent py-2 px-4 rounded-[0.5rem] bg-white not-first:mt-2',
						{
							'border-grey-2 shadow-md text-foregrund': value === corridors
						}
					)}
				>
					<div class="flex-auto">
						<div class="font-bold">{label}</div>
						{#if description}
							<div class="text-sm leading-snug">
								{description}
							</div>
						{/if}
					</div>
					{#if value === corridors}
						<CheckIcon class="flex-none size-4" />
					{/if}
				</div>
			{/each}
		</div>
	{/if}

	{#if type === 'subwatershed'}
		<div class="text-grey-9 text-sm mt-8 pt-8 border-t border-t-grey-2">
			Subwatershed boundary is based on the
			<a
				href="https://www.usgs.gov/national-hydrography/watershed-boundary-dataset"
				target="_blank"
			>
				National Watershed Boundary Dataset
			</a>
			(2023), U.S. Geological Survey.
		</div>
	{:else if type === 'marine hex'}
		<div class="text-grey-9 text-sm mt-8 pt-8 border-t border-t-grey-2">
			Hexagon boundary is based on 40 km<sup>2</sup> hexagons developed by the
			<a href="https://www.sciencebase.gov/catalog/item/5ba9378fe4b08583a5ca0937" target="_blank">
				U.S. Environmental Protection Agency
			</a>
			and extended into the Gulf of America by the
			<a href="https://www.boem.gov/gommapps" target="_blank">
				Gulf of Mexico Marine Assessment Program for Protected Species
			</a>
			(GoMMAPPS). Gulf of America hexagons provided by the NOAA Southeast Fisheries Science Center. Similar
			hexagons were generated in the U.S. Caribbean for internal use by the Southeast Conservation Adaptation
			Strategy (2023).
		</div>
	{/if}

	<NeedHelp />
</section>
