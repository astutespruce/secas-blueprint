import React from 'react'
import PropTypes from 'prop-types'

import { scaleLinear } from 'd3-scale'

import { extent } from 'util/data'
import { formatNumber } from 'util/format'

import Area from './line/Area'
import Line from './line/Line'
import Points from './line/Points'
import XAxis from './line/XAxis'
import YAxis from './line/YAxis'

const UrbanChart = ({ data, width, height }) => {
  const margin = { left: 60, right: 10, top: 16, bottom: 50 }
  const splitIndex = 8 // split at 2019
  const colors = ['#666666', '#D90000']

  const [minX, maxX] = extent(data.map(({ x }) => x))
  // minY is always set to 0
  const maxY = extent(data.map(({ y }) => y))[1]

  // project points into the drawing area
  // (note that scales are flipped here so that 0,0 is bottom left)
  const xScale = scaleLinear()
    .domain([minX, maxX])
    .range([0, width - margin.right - margin.left])
    .nice()

  // Y scale always starts at 0
  const yScale = scaleLinear()
    .domain([0, maxY])
    .range([height - margin.bottom, margin.top])
    .nice()

  const points = data.map(({ x, y, ...rest }) => ({
    ...rest,
    x: xScale(x),
    y: yScale(y),
    yLabel: `${x}: ${formatNumber(y)}`,
  }))

  // only show every other tick
  const xAxisTicks = xScale
    .ticks(6)
    .map((x, i) => ({ x: xScale(x), label: i % 2 === 0 ? x : '' }))

  const yAxisTicks = yScale
    .ticks(5)
    .map((y) => ({ y: yScale(y), label: formatNumber(y) }))

  const leftPoints = points.slice(0, splitIndex)
  // start right points at 2019
  const rightPoints = points.slice(splitIndex - 1)

  return (
    <svg
      style={{
        display: 'block',
        overflow: 'visible',
      }}
      viewBox={`0 0 ${width} ${height}`}
    >
      <g transform={`translate(${margin.left},${margin.top})`}>
        {/* areas */}
        <Area
          points={leftPoints}
          baseline={yScale(0)}
          fill={colors[0]}
          fillOpacity={0.6}
        />
        <Area
          points={rightPoints}
          baseline={yScale(0)}
          fill={colors[1]}
          fillOpacity={0.6}
        />

        {/* axis */}
        <g transform={`translate(0, ${height - margin.bottom})`}>
          <XAxis
            ticks={xAxisTicks}
            label="Decade"
            labelOffset={40}
            fontSize={10}
          />
        </g>
        <YAxis
          ticks={yAxisTicks}
          label="Percent of area"
          labelOffset={48}
          fontSize={10}
        />

        {/* lines */}
        <Line points={leftPoints} stroke={colors[0]} strokeWidth={1} />
        <Line points={rightPoints} stroke={colors[1]} strokeWidth={1} />

        {/* dividing line */}

        <line
          x1={xScale(2019)}
          y1={yScale(0)}
          x2={xScale(2019)}
          y2={yScale(maxY) - 22}
          stroke="#AAA"
        />

        <text
          x={xScale(2019) - 8}
          y={yScale(maxY) - 12}
          textAnchor="end"
          fontSize={10}
          fill="#777"
          className="label"
        >
          Past trend
        </text>

        <text
          x={xScale(2020) + 2}
          y={yScale(maxY) - 12}
          textAnchor="start"
          fontSize={10}
          fill="#777"
          className="label"
        >
          Future trend
        </text>

        {/* render in reverse order so that tooltips show properly with increasing trends */}
        <Points
          points={rightPoints.slice(1)}
          radius={4}
          strokeWidth={0}
          fill={colors[1]}
          baseline={yScale(0)}
        />
        <Points
          points={leftPoints}
          radius={4}
          strokeWidth={0}
          fill={colors[0]}
          baseline={yScale(0)}
        />
      </g>
    </svg>
  )
}

UrbanChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      x: PropTypes.number.isRequired,
      y: PropTypes.number.isRequired,
      label: PropTypes.string,
    })
  ).isRequired,
  width: PropTypes.number,
  height: PropTypes.number,
}

UrbanChart.defaultProps = {
  width: null,
  height: null,
}

export default UrbanChart
