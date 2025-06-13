<script lang="ts">
	import { DEPLOY_ENV } from '$lib/env'
	import { Root as Alert } from '$lib/components/ui/alert'
	import SECASLogo from '$images/SECAS_logo.svg'

	const isStaging = DEPLOY_ENV === 'staging'
</script>

<div class="overflow-y-auto px-4 h-full pt-2 pb-8">
	{#if isStaging}
		<Alert variant="destructive" class="text-md my-4">
			<b>WARNING</b>: this is a test version of this application used for verifying recent changes;
			it is not intended for general use.
		</Alert>
	{/if}

	<p class="text-lg">
		The Southeast Conservation Blueprint is the primary product of the{' '}
		<a href="https://secassoutheast.org/" target="_blank">
			Southeast Conservation Adaptation Strategy
		</a>
		(SECAS). It is a living, spatial plan to achieve the SECAS vision of a connected network of lands
		and waters across the Southeast and Caribbean. The Blueprint is regularly updated to incorporate
		new data, partner input, and information about on-the-ground conditions.
		<br />
		<br />
		For more information, visit the
		<a href="https://secassoutheast.org/blueprint" target="_blank"> Blueprint webpage </a>. To view
		the Blueprint data and make maps, visit the{' '}
		<a href="https://secas-fws.hub.arcgis.com/pages/blueprint" target="_blank">
			Blueprint page of the SECAS Atlas
		</a>.
		<br />
		<br />
		The <b>Southeast Conservation Blueprint Explorer</b> is an online viewer designed to help you understand
		the Blueprint and discover how your area of interest scores on the Blueprint priorities, hubs and
		corridors, indicators, threats, and more. Here, you can:
	</p>

	<ul class="text-lg list-disc pl-6 mt-1 [&>li]:pb-2">
		<li>
			<b>Summarize data</b> to show charts and information for a subwatershed or marine hexagon
		</li>
		<li>
			<b>View point data</b> to discover what is driving the Blueprint priorities and show values at
			a specific location for indicators, threats, and more
		</li>
		<li>
			<b>Filter the Blueprint</b> to find your part of the Blueprint by showing only areas that score
			within a certain range on indicators and other data
		</li>
		<li>
			<b>Upload a shapefile</b> to create detailed custom reports of the Blueprint, hubs and corridors,
			underlying indicators, and threats in your area
		</li>
	</ul>

	<p class="text-lg mt-2">
		<a href="/help" target="_blank" rel="noreferrer">
			Read instructions on how to use this viewer
		</a>.
	</p>

	<hr class="my-8" />

	<div class="flex flex-wrap lg:flex-nowrap gap-4 leading-snug">
		<div class="flex-none">
			<img src={SECASLogo} class="w-[64px]" alt="SECAS logo" />
		</div>
		<div class="flex-auto">
			<p>
				<b>Citation:</b> Southeast Conservation Adaptation Strategy (SECAS). 2024. Southeast
				Conservation Blueprint 2024.{' '}
				<a href="http://secassoutheast.org/blueprint" target="_blank">
					http://secassoutheast.org/blueprint
				</a>.
			</p>
		</div>
	</div>
	<p class="mt-4 leading-snug">
		This application was developed by{' '}
		<a href="https://astutespruce.com" target="_blank"> Astute Spruce, LLC </a>{' '}
		in partnership with the U.S. Fish and Wildlife Service under the{' '}
		<a href="http://secassoutheast.org/" target="_blank">
			Southeast Conservation Adaptation Strategy
		</a>.
	</p>
</div>
