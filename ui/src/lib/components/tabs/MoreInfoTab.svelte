<script lang="ts">
	import { cn } from '$lib/utils'

	import { PARCAs, ProtectedAreas, SLR, Urban, WildfireRisk } from './moreinfo'
	import { NeedHelp } from './general'

	const {
		type,
		slr,
		urban,
		wildfireRisk,
		regions,
		protectedAreas,
		protectedAreasList,
		numProtectedAreas,
		parcas,
		class: className = ''
	} = $props()
</script>

<section class={cn('flex-auto overflow-y-auto h-full py-8 pl-4 pr-8', className)}>
	{#if type === 'pixel' || type === 'subwatershed'}
		<PARCAs {type} {parcas} />
	{/if}

	<ProtectedAreas {type} {protectedAreas} {protectedAreasList} {numProtectedAreas} />

	{#if type === 'pixel' || type === 'subwatershed'}
		<SLR {type} {...slr} />

		<Urban {type} {urban} {regions} />

		<WildfireRisk {type} {wildfireRisk} {regions} />
	{/if}

	<NeedHelp />
</section>
