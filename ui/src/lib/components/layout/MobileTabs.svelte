<script lang="ts">
	import InfoIcon from '~icons/fa-solid/info-circle'
	import MapIcon from '~icons/fa-solid/map'
	import SearchIcon from '~icons/fa-solid/search-location'
	import QuestionIcon from '~icons/fa-solid/question-circle'
	import EnvelopeIcon from '~icons/fa-solid/envelope'
	import PieChartIcon from '~icons/fa-solid/chart-pie'
	import TasksIcon from '~icons/fa-solid/tasks'
	import LineChartIcon from '~icons/fa-solid/chart-line'
	import { Button } from '$lib/components/ui/button'
	import { cn } from '$lib/utils'

	const { tab, hasMapData, onChange } = $props()

	const defaultTabs = [
		{ id: 'info', label: 'Info', icon: InfoIcon },
		{ id: 'map', label: 'Map', icon: MapIcon },
		{ id: 'find', label: 'Find Location', icon: SearchIcon },
		{ id: 'contact', label: 'Contact', icon: EnvelopeIcon }
	]

	const dataTabs = [
		{ id: 'mobile-selected-map', label: 'Map', icon: MapIcon },
		{ id: 'selected-priorities', label: 'Priorities', icon: PieChartIcon },
		{ id: 'selected-indicators', label: 'Indicators', icon: TasksIcon },
		{ id: 'selected-more-info', label: 'More info', icon: LineChartIcon }
	]

	const tabs = hasMapData ? dataTabs : defaultTabs

	const handleClick = (id: string) => () => {
		onChange(id)
	}
</script>

<div class="md:hidden flex-none border-t border-t-grey-9 leading-snug">
	<nav class="grid auto-cols-fr grid-flow-col gap-0 items-center">
		{#each tabs as { id, label, icon: Icon }}
			<Button
				class={cn(
					'flex flex-col gap-0 items-center justify-center text-center flex-grow p-2 h-10 select-none rounded-none text-grey-1 text-[10px]',
					{
						'text-white': id === tab,
						'bg-blue-9': id === tab
					}
				)}
				onclick={handleClick(id)}
			>
				<Icon class="size-3.5" />
				{label}
			</Button>
		{/each}
	</nav>
</div>
