<script lang="ts">
	import { browser } from '$app/environment'
	import PrintIcon from '~icons/fa-solid/file-import'
	import { Root, Trigger, Content, Header, Title, Footer, Close } from '$lib/components/ui/dialog'
	import { Button } from '$lib/components/ui/button'

	let open = $state(false)

	const handlePrint = () => {
		if (browser) {
			window.print()
		}
		open = false
	}
</script>

<Root bind:open>
	<Trigger>
		{#snippet child({ props })}
			<Button {...props} variant="ghost" class="hover:bg-transparent h-auto p-1!">
				<PrintIcon />
				<b>Print / Save to PDF</b>
			</Button>
		{/snippet}
	</Trigger>
	<Content class="pt-4 pb-6 print:hidden">
		<Header class="border-b pb-4 border-b-grey-3">
			<Title class="text-3xl">Print map / save to PDF</Title>
		</Header>
		<p class="text-lg">
			This will use your browser's print interface to save a lightweight capture of your map and any
			enabled filters.
			<br /><br />
			In your browser's print dialog, you can choose to save this to PDF instead of printing it.
		</p>
		<Footer class="border-t border-t-grey-2 pt-2">
			<Close class="text-lg cursor-pointer">Cancel</Close>
			<Button onclick={handlePrint} class="text-lg">Print / Save to PDF</Button>
		</Footer>
	</Content>
</Root>
