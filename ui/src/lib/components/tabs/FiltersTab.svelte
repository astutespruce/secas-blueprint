<script lang="ts">
	import { getContext } from 'svelte'

	import Filter from '~icons/fa-solid/filter'
	import TimesCircle from '~icons/fa-solid/times-circle'
	import { Button } from '$lib/components/ui/button'
	import { defaultFilters } from '$lib/config/filters'
	import type { MapData } from '$lib/types'
	import { cn } from '$lib/utils'

	// TODO: can also derive these from context
	// const { numFilters, onResetFilters } = $props()

	const mapData: MapData = getContext('map-data')

	const numFilters = Object.values(mapData.filters).filter(({ enabled }) => enabled).length

	const handleResetFilters = () => {
		console.log('reset filters')
		mapData.filters = defaultFilters
	}
</script>

<div class="flex justify-between flex-none pt-4 pb-2 px-2 border-b border-b-grey-3">
	<div class="flex items-center gap-2">
		<Filter width="1.5rem" height="1.5rem" />
		<h3>Filter the Blueprint</h3>
	</div>
	<div
		class={cn('flex justify-end items-center', {
			hidden: numFilters > 0
		})}
	>
		<Button onclick={handleResetFilters} class="text-sm py-1 px-2 gap-1">
			<TimesCircle width="1em" height="1em" />
			reset {numFilters} filter{numFilters > 1 ? 's' : ''}
		</Button>
	</div>
</div>

<div class="h-full overflow-y-auto">TODO: tabcontent for filter tab</div>
