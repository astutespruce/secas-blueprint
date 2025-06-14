<script lang="ts">
	import QuestionCircle from '~icons/fa-regular/question-circle'
	import { Provider, Root, Trigger, Content } from '$lib/components/ui/tooltip'

	const { title, description } = $props()
</script>

<Provider delayDuration={0}>
	<Root disableHoverableContent>
		<Trigger>
			<QuestionCircle
				width="1.25rem"
				height="1.25rem"
				class="cursor-pointer text-grey-4 hover:text-grey-9"
			/>
		</Trigger>
		<Content side="right" sideOffset={2} class="pt-2 pb-4 px-3 max-w-[28rem]">
			<h4 class="text-[1rem]">
				{title}
			</h4>
			<p class="text-[0.9rem] leading-tight">
				{description}
			</p>
		</Content>
	</Root>
</Provider>
