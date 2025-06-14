<script lang="ts">
	import Filter from './Filter.svelte'

	const { id, icon, label, color, borderColor, entries, filters, onChange } = $props()

	const visibleEntries = entries.filter(
		({ id: entryId, canBeVisible }) => canBeVisible || filters[entryId].enabled
	)
</script>

<div class="w-full flex-none">
	<!-- header  -->
	<div class={`py-4 md:py-2 px-3 border-b border-t ${color} ${borderColor}`}>
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2">
				<img src={icon} alt={`${label} icon`} class="w-[2em] h-[2em] bg-white rounded-full" />
				<h4 class="text-lg">{label}</h4>
			</div>
		</div>
	</div>

	<!-- filters list -->
	<div class="mb-4">
		{#if visibleEntries.length > 0}
			{#each visibleEntries as entry}
				<Filter {...entry} {...filters[entry.id]} {onChange} />
			{/each}
		{:else}
			<if class="mt-4 text-grey-8 text-center"> no filters available for this area </if>
		{/if}
	</div>
</div>
