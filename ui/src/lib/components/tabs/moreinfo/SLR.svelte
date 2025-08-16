<script lang="ts">
	import { slrNodata } from '$lib/config/constants'
	import { formatPercent } from '$lib/util/format'
	import SLRChart from './SLRChart.svelte'

	const { type, depth, nodata } = $props()

	const { nodataValue, nodataItems } = $derived.by(() => {
		let value = null
		const items = []

		if (type !== 'pixel') {
			for (let i = 0; i < 3; i += 1) {
				// if mostly a single type of nodata, just return that
				if (nodata[i] >= 99) {
					value = i
				}
				if (nodata[i] > 1) {
					items.push(
						`${slrNodata[i].label
							.toLowerCase()
							.replace(/this area is/g, '')
							.replace(/for this area/g, '')
							.trim()} (${formatPercent(nodata[i])}% of area)`
					)
				}
			}
		}

		return { nodataValue: value, nodataItems: items }
	})
</script>

<div class="not-first:mt-8 not-first:border-t not-first:border-t-grey-2 not-first:pt-8">
	<h3 class="text-2xl">Sea Level Rise</h3>

	{#if type === 'pixel'}
		{#if nodata !== null}
			<div>{slrNodata[nodata].label}.</div>
		{:else if depth === null}
			<div>{slrNodata[2].label}.</div>
		{:else if depth === 0}
			<div>This area is already inundated.</div>
		{:else}
			<div>
				This area is projected to be inundated at{' '}
				<b>
					{depth}
					{depth === 1 ? 'foot' : 'feet'}
				</b>{' '}
				of sea-level rise.
			</div>
		{/if}
	{/if}

	<!-- split at top-level into 2 conditional trees for cleaner logic -->
	{#if type !== 'pixel'}
		{#if nodataValue !== null}
			<div>{slrNodata[nodataValue].label}.</div>
		{:else if !(depth && depth.length > 0)}
			<div>{slrNodata[2].label}.</div>
		{:else}
			<div class="text-grey-8 leading-tight">
				Extent of flooding by projected sea level rise within this subwatershed:
			</div>
			<SLRChart data={depth.map((y: number, i: number) => ({ x: i, y }))} />

			{#if nodataItems.length > 0}
				<div class="mt-8 text-grey-8 leading-tight">
					This subwatershed has additional areas not included in the chart above: {nodataItems.join(
						', '
					)}.
				</div>
			{/if}
		{/if}
	{/if}

	<div class="mt-8 text-grey-8 leading-tight">
		Sea level rise estimates derived from the
		<a href="https://coast.noaa.gov/digitalcoast/data/slr.html" target="_blank">
			NOAA sea-level rise inundation data
		</a>. To explore additional SLR information, please see NOAA&apos;s
		<a href="https://coast.noaa.gov/slr/" target="_blank"> Sea Level Rise Viewer </a>.
	</div>
</div>
