<script lang="ts">
	import CaretDown from '~icons/fa-solid/caret-down'
	import CaretRight from '~icons/fa-solid/caret-right'
	import BlueprintIcon from '$images/blueprint.svg'
	import FreshwaterIcon from '$images/f.svg'
	import MarineIcon from '$images/m.svg'
	import OtherInfoIcon from '$images/otherInfo.svg'
	import TerrestrialIcon from '$images/t.svg'
	import { cn } from '$lib/utils'

	import {
		blueprint,
		corridors,
		indicatorGroups,
		indicatorsIndex,
		urbanByDecade,
		slrDepth,
		slrProj,
		wildfireRisk,
		protectedAreas,
		parcas
	} from '$lib/config/constants'
	import { Button } from '$lib/components/ui/button'
	import { Checkbox } from '$lib/components/ui/checkbox'
	import * as Collapsible from '$lib/components/ui/collapsible'
	import { Label } from '$lib/components/ui/label'
	import { InfoTooltip } from '$lib/components/tooltip'

	const priorityDatasets = [blueprint, corridors]
	// polygon versions of PARCAs and protected areas are automatically included
	// when their raster versions are included and not itemized individually
	const otherInfoDatasets = [parcas, protectedAreas, slrDepth, slrProj, urbanByDecade, wildfireRisk]

	const indicatorGroupIcons = {
		f: FreshwaterIcon,
		m: MarineIcon,
		t: TerrestrialIcon
	}

	type Props = {
		availableDatasets: Record<string, boolean>
		selectedDatasets: Record<string, boolean>
	}

	let { availableDatasets, selectedDatasets = $bindable() }: Props = $props()

	let openCategories: Record<string, boolean> = $state({
		priorities: true,
		...Object.fromEntries(indicatorGroups.map(({ id }) => [id, true])),
		otherInfo: true
	})

	const categories = $derived.by(() => {
		// always show all priority datasets; by definition they must be present
		const out = [
			{
				id: 'priorities',
				icon: BlueprintIcon,
				label: 'Priorities',
				color: '#4d004b0d',
				borderColor: '#4d004b2b',
				datasets: priorityDatasets
			}
		]

		indicatorGroups.forEach(({ id, label, color, borderColor, indicators }) => {
			const indicatorsPresent = indicators
				.filter((indicatorId) => availableDatasets[indicatorId])
				.map((indicatorId) => indicatorsIndex[indicatorId])
			if (indicatorsPresent.length > 0) {
				out.push({
					id,
					icon: indicatorGroupIcons[id as keyof typeof indicatorGroupIcons],
					label: `${label} indicators`,
					color,
					borderColor,
					datasets: indicatorsPresent
				})
			}
		})

		// only show the other info datasets that are present, and omit the category if not
		const otherInfoDatasetsPresent = otherInfoDatasets.filter(({ id }) => availableDatasets[id])
		if (otherInfoDatasetsPresent.length > 0) {
			out.push({
				id: 'otherInfo',
				icon: OtherInfoIcon,
				label: 'More info',
				color: '#f3c6a830',
				borderColor: '#f3c6a891',
				datasets: otherInfoDatasetsPresent
			})
		}

		return out
	})

	const handleSelectAll = () => {
		Object.entries(availableDatasets).forEach(([id]) => {
			selectedDatasets[id] = true
		})
	}

	const handleSelectNone = () => {
		Object.entries(availableDatasets).forEach(([id]) => {
			selectedDatasets[id] = false
		})
	}
</script>

<div>
	<div class="sm:flex gap-4">
		<div class="text-2xl font-bold">Choose datasets to include:</div>
		<div class="flex items-center gap-2 flex-none justify-end">
			<Button variant="link" class="p-0 text-base" onclick={handleSelectAll}>select all</Button>
			<div class="text-grey-2">|</div>
			<Button variant="link" class=" p-0 text-base" onclick={handleSelectNone}>select none</Button>
		</div>
	</div>

	<p>
		Choose the datasets you want to include in your analysis from the following datasets that
		overlap your analysis units. You may only choose from datasets that overlap; other datsets are
		not shown here.
	</p>

	<div class="mt-6">
		{#each categories as category (category.id)}
			<Collapsible.Root
				bind:open={openCategories[category.id]}
				class="not-first-of-type:mt-2 not-last-of-type:mb-8"
			>
				<Collapsible.Trigger
					class="w-full py-2 border-t border-b items-center flex gap-2 text-start px-2 cursor-pointer"
					style={`background-color: ${category.color}; border-color: ${category.borderColor}`}
				>
					{#if openCategories[category.id]}
						<CaretDown class="size-6" aria-hidden="true" />
					{:else}
						<CaretRight class="size-6" aria-hidden="true" />
					{/if}
					<img src={category.icon} alt="" aria-hidden="true" class="size-8" />
					<div class="font-bold text-xl">
						{category.label}
					</div>
				</Collapsible.Trigger>
				<Collapsible.Content class="mt-2">
					{#each category.datasets as dataset (dataset.id)}
						<div class="flex items-center gap-2">
							<Checkbox
								id={dataset.id}
								aria-label={`Select / deselect ${dataset.label}`}
								class="cursor-pointer size-5 rounded-xs disabled:border-grey-8/50 border-2 [&_svg]:size-4"
								bind:checked={selectedDatasets[dataset.id]}
								disabled={!availableDatasets[dataset.id]}
							/>
							<Label
								for={dataset.id}
								class={cn('text-base cursor-pointer', {
									'italic opacity-100! text-grey-8 cursor-not-allowed':
										!availableDatasets[dataset.id]
								})}
								>{dataset.label}
								{#if !availableDatasets[dataset.id]}
									<span class="text-sm"> (no data available) </span>
								{/if}
							</Label>
							<div class="mt-2">
								<InfoTooltip
									title={dataset.label}
									description={dataset.description}
									aria-label={`Show details for ${dataset.label}`}
								/>
							</div>
						</div>
					{/each}
				</Collapsible.Content>
			</Collapsible.Root>
		{/each}
	</div>
</div>

<!-- <FilterGroup
					label="Filter by priorities"
					icon={BlueprintIcon}
					color="#4d004b0d"
					borderColor="#4d004b2b"
					entries={priorityFilters}
					onChange={handleFilterChange}
				/>

				{#each indicatorGroups as { id, label, color, borderColor } (id)}
					<FilterGroup
						label={`Filter by ${label.toLowerCase()}`}
						icon={indicatorGroupIcons[id as keyof typeof indicatorGroupIcons]}
						{color}
						{borderColor}
						entries={indicatorGroupFilters[id as keyof typeof indicatorGroupFilters]}
						onChange={handleFilterChange}
					/>
				{/each}

				<FilterGroup
					label="More filters"
					icon={OtherInfoIcon}
					color="#f3c6a830"
					borderColor="#f3c6a891"
					entries={otherInfoFilters}
					onChange={handleFilterChange}
				/> -->
