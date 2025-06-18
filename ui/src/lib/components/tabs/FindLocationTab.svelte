<script lang="ts">
	import { getContext } from 'svelte'

	import LocationArrowIcon from '~icons/fa-solid/location-arrow'
	import SpinnerIcon from '~icons/fa-solid/spinner'
	import { Search } from '$lib/components/search'
	import { Button } from '$lib/components/ui/button'
	import { hasGeolocation } from '$lib/util/dom'
	import type { LocationData } from '$lib/types'

	const navigatorOptions = {
		enableHighAccuracy: false,
		maximumAge: 0,
		timeout: 6000
	}

	let isError: boolean = $state(false)
	let isPending: boolean = $state(false)
	const locationData: LocationData = getContext('location-data')

	const handleGetMyLocation = () => {
		isError = false
		isPending = true

		navigator.geolocation.getCurrentPosition(
			({ coords: { latitude, longitude } }) => {
				isPending = false
				locationData.location = {
					latitude,
					longitude
				}
			},
			(err) => {
				isError = true
				isPending = false
				console.error(err)
			},
			navigatorOptions
		)
	}
</script>

<section class="flex flex-col h-full justify-between overflow-y-auto pt-4 pb-8">
	<div class="flex-auto">
		<h3 class="mb-2 pl-4 pr-8 text-xl">Find a location on the map</h3>
		<div
			class="[&_.search-input-container]:px-4 [&_.search-input-container]:py-2 [&_.search-input-container]:bg-grey-1"
		>
			<Search />
		</div>
	</div>

	<div class="flex-none">
		{#if hasGeolocation}
			{#if isPending}
				<div class="flex justify-center text-grey-8 px-4 gap-4">
					<SpinnerIcon class="size-6 animate-spin" />
					Fetching your location from your device
				</div>
			{:else}
				<div class="flex flex-col items-center mt-8">
					<Button onclick={handleGetMyLocation} class="text-lg">
						<LocationArrowIcon class="size-5" />
						Go to my location
					</Button>
				</div>

				{#if isError}
					<div class="text-grey-8 mt-8 px-4">
						We&apos;re sorry, there was an error trying to get your current location. Your browser
						may not have sufficient permissions on your device to determine your location. You can
						also try again.
					</div>
				{/if}
			{/if}
		{/if}
	</div>
</section>
