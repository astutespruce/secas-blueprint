<script lang="ts">
	import { scaleLinear } from 'd3-scale'
	import { area, line } from 'd3-shape'

	import { Points, XAxis, YAxis } from '$lib/components/chart'
	import type { Point } from '$lib/types'
	import { extent } from '$lib/util/data'
	import { formatNumber } from '$lib/util/format'

	type Props = {
		data: Point[]
	}

	const { data }: Props = $props()

	let clientWidth: number | undefined = $state()

	const height = 200
	const margin = { left: 60, right: 10, top: 10, bottom: 50 }

	const [minX, maxX] = $derived(extent(data.map(({ x }) => x)))
	// minY is always set to 0
	const maxY = $derived(extent(data.map(({ y }: { y: number }) => y))[1])

	// project points into the drawing area
	// (note that scales are flipped here so that 0,0 is bottom left)
	const xScale = $derived(
		scaleLinear()
			.domain([minX, maxX])
			.range([0, (clientWidth || 300) - margin.right - margin.left])
			.nice()
	)

	// Y scale always starts at 0
	const yScale = $derived(
		scaleLinear()
			.domain([0, maxY])
			.range([height - margin.bottom, margin.top])
			.nice()
	)

	const points = $derived(
		data.map(({ x, y, ...rest }) => ({
			...rest,
			x: xScale(x),
			y: yScale(y),
			yLabel: `${x}: ${formatNumber(y)}`
		}))
	)

	const xAxisTicks = $derived(
		xScale.ticks(data.length).map((x, i) => ({ x: xScale(x), label: formatNumber(x) }))
	)

	const yAxisTicks = $derived(
		yScale.ticks(5).map((y) => ({ y: yScale(y), label: formatNumber(y) }))
	)
</script>

<div bind:clientWidth class={`h-[${height}px] w-full`}>
	<svg viewBox={`0 0 ${clientWidth || 300} ${height}`} class="w-full overflow-visible">
		<g transform={`translate(${margin.left},${margin.top})`}>
			<!-- area -->
			<path
				d={area()
					.x0(({ x }: Point) => x)
					.y0(yScale(0))
					.y1(({ y }: Point) => y)(points)}
				fill="#004da8"
				fill-opacity="0.6"
			/>

			<!-- axis -->
			<g transform={`translate(0, ${height - margin.bottom})`}>
				<XAxis ticks={xAxisTicks} label="Amount of sea level rise (feet)" labelOffset={40} />
			</g>
			<YAxis ticks={yAxisTicks} label="Percent of area" labelOffset={48} />

			<!-- line -->
			<path
				d={line()(points.map(({ x, y }) => [x, y]))}
				fill="none"
				stroke-width={2}
				stroke="#004da8"
			/>

			<!-- render in reverse order so that tooltips show properly with increasing trends -->
			<Points {points} minX={xAxisTicks[0]} radius={4} fill="#004da8" baseline={yScale(0)} />
		</g>
	</svg>
</div>
