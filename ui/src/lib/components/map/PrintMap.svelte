<script lang="ts">
	import { LegendElement } from './legend'

	const { src, title, subtitle, categories } = $props()
</script>

{#if src !== null}
	<div class="mt-4 hidden print:block">
		<img {src} class="block max-h-180 max-w-190 border border-grey-5 flex-none m-px" alt="map" />

		<div class="text-muted-foreground text-xs [&_a]:text-muted-foreground">
			Basemap credits: © <a href="https://www.mapbox.com/about/maps/">Mapbox</a> ©
			<a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>
			<a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this basemap</a>
		</div>

		<div class="break-inside-avoid flex-auto mt-4">
			<div class="flex-auto font-bold leading-none text-lg">
				{title}
			</div>

			{#if subtitle}
				<div class="font-normal text-grey-8 leading-none text-[15px] mt-1 mb-3">
					{subtitle}
				</div>
			{/if}

			<div class="mt-2">
				{#each categories as element (element.label)}
					<LegendElement {...element} />
				{/each}
			</div>
		</div>
	</div>
{/if}
