<script lang="ts">
	import CheckIcon from '~icons/fa-solid/check'
	import { PercentBarChart } from '$lib/components/chart'
	import { wildfireRisk as categories } from '$lib/config/constants'
	import { cn } from '$lib/utils'

	const { type, wildfireRisk, regions } = $props()

	const bars = $derived(
		categories.map((category) => ({
			...category,
			percent: wildfireRisk ? wildfireRisk[category.value] || 0 : 0
		}))
	)
</script>

<div class="not-first:mt-8 not-first:border-t not-first:border-t-grey-2 not-first:pt-8">
	<h3 class="text-2xl">Wildfire Likelihood</h3>

	{#if type === 'pixel'}
		{#if wildfireRisk === null}
			<div class="text-grey-8">
				Wildfire likelihood data is not currently available for this area.
			</div>
		{:else}
			<div class="text-grey-8">Annual burn probability:</div>

			<div class="ml-2 mt-2">
				{#each categories as { value, label }}
					<div
						class="flex items-baseline justify-between pl-2 border-b border-b-grey-2 pb-1 not-first:mt-1 gap-4"
					>
						<div
							class={cn('flex-auto text-grey-8', {
								'text-foreground font-bold': value === wildfireRisk
							})}
						>
							{label}
						</div>
						<CheckIcon
							class={cn('size-4 flex-none invisible', { visible: value === wildfireRisk })}
						/>
					</div>
				{/each}
			</div>
		{/if}
	{/if}

	{#if type !== 'pixel'}
		{#if (regions && regions.has('caribbean')) || wildfireRisk === null}
			<div class="text-grey-8">
				Wildfire likelihood data is not currently available for this area.
			</div>
		{:else}
			<div class="text-grey-8 leading-tight">
				Area in each wildfire probability category within this subwatershed:
			</div>
			<div class="mt-4">
				{#each bars as bar}
					<PercentBarChart {...bar} class="mt-2 mb-4" />
				{/each}
			</div>
		{/if}
	{/if}

	<!-- don't show data info in Caribbean -->
	{#if !(regions && regions.has('caribbean'))}
		<div class="mt-8 text-grey-8 leading-tight">
			Wildfire likelihood data derived from the{' '}
			<a href="https://wildfirerisk.org/" target="_blank"> Wildfire Risk to Communities </a>{' '}
			project by the USDA Forest Service.
		</div>
	{/if}
</div>
