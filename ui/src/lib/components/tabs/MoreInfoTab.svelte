<script lang="ts">
	import { cn } from '$lib/utils'

	import { ProtectedAreas, SLR, Urban, WildfireRisk } from './moreinfo'
	import { NeedHelp } from './general'

	const {
		type,
		slr,
		urban,
		wildfireRisk,
		subregions,
		protectedAreas,
		protectedAreasList,
		numProtectedAreas,
		class: className = ''
	} = $props()
</script>

<section class={cn('flex-auto overflow-y-auto h-full py-8 pl-4 pr-8', className)}>
	{#if type === 'pixel' || type === 'subwatershed'}
		<Urban {type} {urban} {subregions} />

		<SLR {type} {...slr} />

		<WildfireRisk {type} {wildfireRisk} {subregions} />
	{/if}

	<ProtectedAreas {type} {protectedAreas} {protectedAreasList} {numProtectedAreas} />

	<NeedHelp />
</section>
