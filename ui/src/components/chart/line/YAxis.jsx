import React from 'react'
import PropTypes from 'prop-types'

const YAxis = ({
  ticks,
  label,
  labelOffset,
  stroke,
  strokeWidth,
  fontSize,
  labelColor,
}) => {
  const midpointY = (ticks[ticks.length - 1].y - ticks[0].y) / 2 + ticks[0].y

  return (
    <g>
      <line
        x1={0}
        y1={ticks[0].y}
        x2={0}
        y2={ticks[ticks.length - 1].y}
        stroke={stroke}
        strokeWidth={strokeWidth}
      />

      {label ? (
        <text
          x={-labelOffset}
          y={midpointY}
          textAnchor="middle"
          transform={`rotate(-90 ${-labelOffset} ${midpointY})`}
          fill={labelColor}
          fontSize="larger"
        >
          {label}
        </text>
      ) : null}

      {ticks.map(({ y, label: tickLabel }) => (
        <g key={y} transform={`translate(-4, ${y})`}>
          <line x1={0} y1={0} x2={8} y2={0} stroke={stroke} strokeWidth={1} />

          <text textAnchor="end" x={-4} y={fontSize / 2} fill={labelColor}>
            {tickLabel}
          </text>
        </g>
      ))}
    </g>
  )
}

YAxis.propTypes = {
  ticks: PropTypes.arrayOf(
    PropTypes.shape({
      y: PropTypes.number.isRequired,
      label: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    })
  ).isRequired,

  stroke: PropTypes.string,
  strokeWidth: PropTypes.number,
  fontSize: PropTypes.number,
  label: PropTypes.string,
  labelColor: PropTypes.string,
  labelOffset: PropTypes.number,
}

YAxis.defaultProps = {
  strokeWidth: 1,
  stroke: '#AAA',
  fontSize: 10,
  label: null,
  labelColor: '#666',
  labelOffset: 30,
}

export default YAxis
