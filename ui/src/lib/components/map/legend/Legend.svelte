<script lang="ts">
	import EyeIcon from '~icons/fa-solid/eye'
	import EyeSlashIcon from '~icons/fa-solid/eye-slash'
	import { Button } from '$lib/components/ui/button'

	import LegendElement from './LegendElement.svelte'

	const { title, subtitle, categories, isVisible, onToggleLayerVisibility } = $props()

	let isOpen = $state(true)

	const toggleVisibility = () => {
		isOpen = !isOpen
	}

	const handleKeyDown = ({ target: { role }, key }: { target: { role: string }; key: string }) => {
		if (key === 'Enter' && role === 'button') {
			toggleVisibility()
		}
	}

	const toggleLayerVisibility = (e: Event) => {
		onToggleLayerVisibility()
		e.stopPropagation()
	}
</script>

<div
	class="absolute z-1 text-grey-9 bg-white cursor-pointer bottom-[40px] lg:bottom-[24px] right-[10px] border border-grey-5 rounded-sm shadow-md shadow-grey-6 max-w-[210px] select-none hidden md:block focus-visible:outline-2 outline-accent"
	onclick={toggleVisibility}
	onkeydown={handleKeyDown}
	role="button"
	tabindex={0}
>
	{#if isOpen}
		<div class="p-2" title="Click to hide legend">
			<div class="flex items-top justify-between gap-2">
				<div class="flex-auto font-bold leading-tight">
					{title}
					{#if subtitle}
						<div class="font-normal text-grey-8 leading-none text-sm">
							{subtitle}
						</div>
					{/if}
				</div>
				<Button
					class="flex-none bg-grey-0 text-foreground border border-grey-7 rounded-sm p-0 leading-none hover:bg-grey-1 w-8 h-8"
					title={`Click to ${isVisible ? 'hide' : 'show'}`}
					onclick={toggleLayerVisibility}
					tabindex={0}
				>
					{#if isVisible}
						<EyeIcon class="size-4" />
					{:else}
						<EyeSlashIcon class="size-4" />
					{/if}
				</Button>
			</div>
			<div class="mt-2">
				{#each categories as element}
					<LegendElement {...element} />
				{/each}
			</div>
		</div>
	{:else}
		<div class="py-1 px-2" title="Click to show legend">Show Legend</div>
	{/if}
</div>
