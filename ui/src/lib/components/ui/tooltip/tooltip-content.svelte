<script lang="ts">
	import { Tooltip as TooltipPrimitive } from 'bits-ui'
	import { cn } from '$lib/utils.js'

	let {
		ref = $bindable(null),
		class: className,
		sideOffset = 0,
		side = 'top',
		children,
		arrowClasses,
		...restProps
	}: TooltipPrimitive.ContentProps & {
		arrowClasses?: string
	} = $props()
</script>

<TooltipPrimitive.Portal>
	<TooltipPrimitive.Content
		bind:ref
		data-slot="tooltip-content"
		{sideOffset}
		{side}
		class={cn(
			'bg-white border border-grey-4 drop-shadow-md animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 origin-(--bits-tooltip-content-transform-origin) z-10000 w-fit text-balance rounded-md px-3 py-1.5 text-xs',
			className
		)}
		{...restProps}
	>
		{@render children?.()}
		<TooltipPrimitive.Arrow>
			{#snippet child({ props })}
				<div
					class={cn(
						'z-50 size-0 border-8 border-transparent',
						// 'data-[side=top]:translate-x-1/2 data-[side=top]:translate-y-[calc(-50%_+_2px)]',
						// 'data-[side=bottom]:-translate-y-[calc(-50%_+_1px)] data-[side=bottom]:translate-x-1/2',
						// 'data-[side=right]:translate-x-[calc(50%_+_2px)] data-[side=right]:translate-y-1/2',
						// 'data-[side=left]:translate-y-[calc(50%_-_3px)]',
						'data-[side=right]:border-l-grey-9 data-[side=right]:border-b-grey-9 -rotate-45 data-[side=right]:-mt-1',
						'data-[side=bottom]:border-t-grey-9 data-[side=right]:border-l-grey-9',
						arrowClasses
					)}
					{...props}
				></div>
			{/snippet}
		</TooltipPrimitive.Arrow>
	</TooltipPrimitive.Content>
</TooltipPrimitive.Portal>
