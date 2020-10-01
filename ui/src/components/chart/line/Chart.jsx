import React from 'react'
import PropTypes from 'prop-types'
import { scaleLinear } from 'd3-scale'

import { extent } from 'util/data'
import { formatNumber } from 'util/format'

import Area from './Area'
import Line from './Line'
import Points from './Points'
import XAxis from './XAxis'
import YAxis from './YAxis'

const Chart = ({
  data,
  width,
  height,
  margin,
  xTicks,
  xTickFormatter,
  yTicks,
  yTickFormatter,
  xLabel,
  xLabelOffset,
  yLabel,
  yLabelOffset,
  lineColor,
  lineWidth,
  areaColor,
  areaOpacity,
  pointRadius,
  pointStrokeColor,
  pointStrokeWidth,
  pointColor,
  fontSize,
}) => {
  if (!(width && height)) {
    return null
  }

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
    yLabel: formatNumber(y),
  }))

  const xAxisTicks = xScale
    .ticks(xTicks)
    .map((x) => ({ x: xScale(x), label: xTickFormatter(x) }))

  const yAxisTicks = yScale
    .ticks(yTicks)
    .map((y) => ({ y: yScale(y), label: yTickFormatter(y) }))

  return (
    <svg
      style={{
        display: 'block',
        overflow: 'visible',
      }}
      viewBox={`0 0 ${width} ${height}`}
    >
      <g transform={`translate(${margin.left},${margin.top})`}>
        {areaColor ? (
          <Area
            points={points}
            baseline={yScale(0)}
            fill={areaColor}
            fillOpacity={areaOpacity}
          />
        ) : null}

        <g transform={`translate(0, ${height - margin.bottom})`}>
          <XAxis
            ticks={xAxisTicks}
            label={xLabel}
            labelOffset={xLabelOffset}
            fontSize={fontSize}
          />
        </g>
        <YAxis
          ticks={yAxisTicks}
          label={yLabel}
          labelOffset={yLabelOffset}
          fontSize={fontSize}
        />

        {lineWidth ? (
          <Line points={points} stroke={lineColor} strokeWidth={lineWidth} />
        ) : null}

        {pointRadius ? (
          <Points
            points={points}
            radius={pointRadius}
            stroke={pointStrokeColor}
            strokeWidth={pointStrokeWidth}
            fill={pointColor}
            baseline={yScale(0)}
          />
        ) : null}
      </g>
    </svg>
  )
}

Chart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      x: PropTypes.number.isRequired,
      y: PropTypes.number.isRequired,
      label: PropTypes.string,
    })
  ).isRequired,
  width: PropTypes.number,
  height: PropTypes.number,
  xTicks: PropTypes.number,
  xTickFormatter: PropTypes.func,
  yTicks: PropTypes.number,
  yTickFormatter: PropTypes.func,
  xLabel: PropTypes.string,
  xLabelOffset: PropTypes.number,
  yLabel: PropTypes.string,
  yLabelOffset: PropTypes.number,
  lineColor: PropTypes.string,
  lineWidth: PropTypes.number,
  areaColor: PropTypes.string,
  areaOpacity: PropTypes.number,
  pointStrokeColor: PropTypes.string,
  pointStrokeWidth: PropTypes.number,
  pointColor: PropTypes.string,
  pointRadius: PropTypes.number,
  fontSize: PropTypes.number,
  margin: PropTypes.objectOf(PropTypes.number),
}

Chart.defaultProps = {
  width: null,
  height: null,
  xTicks: null,
  xTickFormatter: formatNumber,
  yTicks: null,
  yTickFormatter: formatNumber,
  xLabel: null,
  xLabelOffset: null,
  yLabel: null,
  yLabelOffset: null,
  lineWidth: 1,
  lineColor: '#AAA',
  areaColor: null,
  areaOpacity: null,
  pointStrokeColor: null,
  pointStrokeWidth: 0,
  pointColor: '#AAA',
  pointRadius: 4,
  fontSize: 10,
  margin: {
    left: 50,
    right: 10,
    bottom: 50,
    top: 10,
  },
}

export default Chart
