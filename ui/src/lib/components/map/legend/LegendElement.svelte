<script lang="ts">
	import { cn } from '$lib/utils'

	const { label, shortLabel, color, outlineColor } = $props()
</script>

<div class="flex items-top leading-none gap-1 text-sm not-first:mt-2">
	<div
		class={cn('flex-none w-5 h-4 rounded-[0.25rem]', { border: !!outlineColor })}
		style={`background-color:${color}bf;`}
	></div>
	{shortLabel || label}
</div>
