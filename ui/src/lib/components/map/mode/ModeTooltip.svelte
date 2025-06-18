<script lang="ts">
	import { Provider, Root, Trigger, Content } from '$lib/components/ui/tooltip'
	import { cn } from '$lib/utils'

	const { content, children, class: className, onClick } = $props()
</script>

<Provider delayDuration={0}>
	<Root disableHoverableContent>
		<Trigger
			class={cn(
				'text-sm md:text-md p-2 not-first:ml-[2px] first:rounded-l-md last:rounded-r-md leading-none min-w-[6em] cursor-pointer',
				className
			)}
			onclick={onClick}
		>
			{@render children()}
		</Trigger>
		<Content side="bottom" class="py-2 px-3 max-w-[240px] z-[10000] hidden md:block">
			<p class="text-[0.9rem] leading-tight">
				{content}
			</p>
		</Content>
	</Root>
</Provider>
