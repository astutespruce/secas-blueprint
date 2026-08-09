<script lang="ts">
	import CheckIcon from '~icons/fa-solid/check'
	import { PercentBarChart } from '$lib/components/chart'
	import { parcas as parcaInfo } from '$lib/config/constants'
	import { cn } from '$lib/utils'

	const { type, parcas = null } = $props()

	const bars = $derived(
		parcaInfo.values.map((category) => ({
			...category,
			percent: parcas ? parcas[category.value] || 0 : 0
		}))
	)
</script>

<div class="not-first:mt-8 not-first:border-t not-first:border-t-grey-2 not-first:pt-8">
	<h3 class="text-2xl">Priority Amphibian and Reptile Conservation Areas</h3>

	{#if type === 'pixel'}
		{#if parcas === null}
			<div class="text-grey-8">
				Priority Amphibian and Reptile Conservation Areas are not currently available for this area.
			</div>
		{:else}
			<div class="ml-2 mt-2">
				{#each parcaInfo.values as { value, label } (value)}
					<div
						class="flex items-baseline justify-between pl-2 border-b border-b-grey-2 pb-1 not-first:mt-1 gap-4"
					>
						<div
							class={cn('flex-auto text-grey-8', {
								'text-foreground font-bold': value === parcas
							})}
						>
							{label}
						</div>

						<CheckIcon class={cn('size-4 flex-none invisible', { visible: value === parcas })} />
					</div>
				{/each}
			</div>
		{/if}
	{:else if parcas === null}
		<div class="text-grey-8">
			Priority Amphibian and Reptile Conservation Areas are not currently available for this area.
		</div>
	{:else}
		{#each bars as bar (bar.value)}
			<PercentBarChart {...bar} class="mt-2 mb-4" />
		{/each}
	{/if}

	{#if parcas !== null}
		<div class="mt-8 text-grey-8 leading-snug">
			Priority Amphibian and Reptile Conservation Areas are derived from data provided by the
			<a href="https://arcprotects.org/work/" target="_blank">Amphibian and Reptile Conservancy</a>.
		</div>
	{/if}
</div>
