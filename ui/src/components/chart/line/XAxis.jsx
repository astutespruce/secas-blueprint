import React from 'react'
import PropTypes from 'prop-types'

const XAxis = ({
  ticks,
  label,
  labelOffset,
  stroke,
  strokeWidth,
  fontSize,
  labelColor,
}) => {
  const midpointX = (ticks[ticks.length - 1].x - ticks[0].x) / 2 + ticks[0].x

  return (
    <g>
      <line
        y1={0}
        x1={ticks[0].x}
        y2={0}
        x2={ticks[ticks.length - 1].x}
        stroke={stroke}
        strokeWidth={strokeWidth}
      />

      {label ? (
        <text
          x={midpointX}
          y={labelOffset}
          textAnchor="middle"
          fill={labelColor}
          fontSize="larger"
        >
          {label}
        </text>
      ) : null}

      {ticks.map(({ x, label: tickLabel }) => (
        <g key={x} transform={`translate(${x}, -4)`}>
          <line x1={0} y1={0} x2={0} y2={8} stroke={stroke} strokeWidth={1} />

          <text textAnchor="middle" x={0} y={fontSize + 12} fill={labelColor}>
            {tickLabel}
          </text>
        </g>
      ))}
    </g>
  )
}

XAxis.propTypes = {
  ticks: PropTypes.arrayOf(
    PropTypes.shape({
      x: PropTypes.number.isRequired,
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

XAxis.defaultProps = {
  strokeWidth: 1,
  stroke: '#AAA',
  fontSize: 10,
  label: null,
  labelColor: '#666',
  labelOffset: 30,
}

export default XAxis
