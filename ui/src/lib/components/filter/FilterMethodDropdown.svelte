<script lang="ts">
	import GearIcon from '~icons/fa-solid/cog'
	import { getContext } from 'svelte'
	import type { MapData } from '$lib/components/map'
	import { Button } from '$lib/components/ui/button'
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu'
	import AndLogicIcon from '$images/AndLogicIcon.svg'
	import OrLogicIcon from '$images/OrLogicIcon.svg'

	const mapData: MapData = getContext('map-data')
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		{#snippet child({ props })}
			<Button {...props} variant="ghost" class="hover:bg-transparent h-auto p-1!">
				<b>Change filter overlay method</b>
				<GearIcon />
			</Button>
		{/snippet}
	</DropdownMenu.Trigger>
	<DropdownMenu.Content class="w-72 text-base">
		<DropdownMenu.Group>
			<DropdownMenu.Label class="text-base">Filter overlay method:</DropdownMenu.Label>
			<DropdownMenu.Separator />
			<DropdownMenu.RadioGroup bind:value={mapData.filterMode}>
				<DropdownMenu.RadioItem value="AND" class="gap-4">
					<img src={AndLogicIcon} alt="AND logic icon" class="size-7" />
					Display only the areas where the selected filters overlap.
				</DropdownMenu.RadioItem>
				<DropdownMenu.RadioItem value="OR" class="gap-4">
					<img src={OrLogicIcon} alt="OR logic icon" class="size-7" />
					Display all areas where any of the selected filters are present.
				</DropdownMenu.RadioItem>
			</DropdownMenu.RadioGroup>
		</DropdownMenu.Group>
	</DropdownMenu.Content>
</DropdownMenu.Root>
