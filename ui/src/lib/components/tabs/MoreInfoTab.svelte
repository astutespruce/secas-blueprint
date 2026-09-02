<script lang="ts">
	import { cn } from '$lib/utils'

	import { PARCAs, ProtectedAreas, SLR, Urban, WildfireRisk } from './moreinfo'
	import { NeedHelp } from './general'

	const {
		type,
		slr,
		urban,
		wildfire_risk,
		regions = new Set(),
		protected_areas,
		protected_areas_list,
		num_protected_areas,
		parcas,
		class: className = ''
	} = $props()

	const showTerrestrialDatasets = $derived(
		regions && (regions.has('continental') || regions.has('caribbean'))
	)
</script>

<section class={cn('flex-auto overflow-y-auto h-full py-8 pl-4 pr-8', className)}>
	{#if showTerrestrialDatasets}
		<PARCAs {type} {parcas} />
	{/if}

	<ProtectedAreas {type} {protected_areas} {protected_areas_list} {num_protected_areas} />

	{#if showTerrestrialDatasets}
		<SLR {type} {...slr} />

		<Urban {type} {urban} {regions} />

		<WildfireRisk {type} {wildfire_risk} />
	{/if}

	<NeedHelp />
</section>
