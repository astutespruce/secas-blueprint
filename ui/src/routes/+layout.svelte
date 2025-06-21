<script lang="ts">
	import sourceSansPro from '@fontsource/source-sans-pro/files/source-sans-pro-latin-400-normal.woff2?url'
	import sourceSansProBold from '@fontsource/source-sans-pro/files/source-sans-pro-latin-900-normal.woff2?url'

	import { Analytics, Footer, Header } from '$lib/components/layout'

	import '../app.css'

	let { children } = $props()
</script>

<svelte:head>
	<link rel="preload" as="font" type="font/woff2" href={sourceSansPro} crossorigin="anonymous" />
	<link
		rel="preload"
		as="font"
		type="font/woff2"
		href={sourceSansProBold}
		crossorigin="anonymous"
	/>
</svelte:head>

<Analytics />

<div class="flex flex-col h-full w-full overflow-none">
	<!-- <Header />

	<div class="h-full w-full flex-auto overflow-auto"> -->
	{@render children()}
	<!-- </div>
	<Footer /> -->
</div>
