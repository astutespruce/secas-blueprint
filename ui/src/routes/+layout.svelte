<script lang="ts">
    import sourceSansPro from '@fontsource/source-sans-pro/files/source-sans-pro-latin-400-normal.woff2?url'
    import sourceSansProBold from '@fontsource/source-sans-pro/files/source-sans-pro-latin-700-normal.woff2?url'

    import '../app.css'

    import { Analytics, Footer, Header } from '$lib/components/layout'

    let { children } = $props()
</script>

<svelte:head>
    <link rel="preload" as="font" type="font/woff2" href={sourceSansPro} crossorigin="anonymous" />
    <link rel="preload" as="font" type="font/woff2" href={sourceSansProBold} crossorigin="anonymous" />
    <link rel="shortcut icon" href="/favicon.ico" />
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
    <link rel="icon" type="image/png" sizes="64x64" href="/favicon-64x64.png" />
    <link rel="icon" type="image/svg" href="/favicon-64x64.svg" />
</svelte:head>

<Analytics />

<div class="flex flex-col h-full w-full overflow-none">
    <Header />

    <div class="h-full w-full flex-auto overflow-auto">
        {@render children()}
    </div>
    <Footer />
</div>