<script lang="ts">
    import { browser } from '$app/environment'
    import { GOOGLE_ANALYTICS_ID } from '$lib/env'

    if (browser && GOOGLE_ANALYTICS_ID) {
        window.dataLayer = window.dataLayer || []

        function gtag() {
            dataLayer.push(arguments)
        }

        gtag('js', new Date())
        gtag('config', GOOGLE_ANALYTICS_ID)
    }
</script>

<svelte:head>
    {#if browser && typeof GOOGLE_ANALYTICS_ID !== 'undefined'}
        <script async src={`https://www.googletagmanager.com/gtag/js?id=${GOOGLE_ANALYTICS_ID}`}></script>
    {/if}
</svelte:head>
