<script lang="ts">
	import { Progress } from '$lib/components/ui/progress'

	const { message, progress } = $props()
</script>

<div class="container mt-4 py-4">
	<h3 class="text-2xl">
		{#if message}
			{message}...
		{:else}
			Creating report...
		{/if}
	</h3>
	<div class="flex items-center gap-6 mt-2">
		<Progress max={100} value={progress} class="h-[1rem]" />
		<div class="text-xl">
			{progress}%
		</div>
	</div>
</div>
