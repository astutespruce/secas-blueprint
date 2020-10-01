import React, { useCallback, useState } from 'react'
import PropTypes from 'prop-types'

const Points = ({
  points,
  baseline,
  radius,
  stroke,
  strokeWidth,
  fill,
  hoverRadius,
  axisDropStroke,
  axisDropStrokeWidth,
}) => {
  const [activeIndex, setActiveIndex] = useState(null)

  const handleMouseOver = useCallback(({ target: { dataset: { index } } }) => {
    setActiveIndex(() => parseInt(index, 10))
  }, [])

  const handleMouseOut = useCallback(() => {
    setActiveIndex(() => null)
  }, [])

  const minX = Math.min(...points.map(({ x }) => x))

  return (
    <g>
      {points.map(({ x, y, yLabel }, i) => (
        <g key={`${x}_${y}`}>
          {activeIndex && activeIndex === i ? (
            <>
              <line
                x1={minX}
                y1={y}
                x2={x}
                y2={y}
                stroke={axisDropStroke}
                strokeWidth={axisDropStrokeWidth}
                strokeDasharray="2 4"
              />
              <circle r={3} cx={minX} cy={y} fill="#666" />
              <line
                x1={x}
                y1={baseline}
                x2={x}
                y2={y}
                stroke={axisDropStroke}
                strokeWidth={axisDropStrokeWidth}
                strokeDasharray="2 4"
              />
              <circle r={3} cx={x} cy={baseline} fill="#666" />
            </>
          ) : null}

          <circle
            r={i === activeIndex ? radius * 2 : radius}
            cx={x}
            cy={y}
            fill={fill}
            stroke={stroke}
            strokeWidth={strokeWidth}
          />

          <circle
            key={`${x}_${y}`}
            r={hoverRadius || radius * 2}
            cx={x}
            cy={y}
            fill="transparent"
            stroke="none"
            style={{ cursor: 'pointer' }}
            data-index={i}
            onMouseEnter={handleMouseOver}
            onMouseLeave={handleMouseOut}
          />

          {i === activeIndex ? (
            <text x={x} y={y - 14} textAnchor="middle">
              {yLabel}
            </text>
          ) : null}
        </g>
      ))}
    </g>
  )
}

Points.propTypes = {
  points: PropTypes.arrayOf(
    PropTypes.shape({
      x: PropTypes.number.isRequired,
      y: PropTypes.number.isRequired,
      label: PropTypes.string,
    })
  ).isRequired,
  baseline: PropTypes.number.isRequired,
  radius: PropTypes.number,
  stroke: PropTypes.string,
  strokeWidth: PropTypes.number,
  fill: PropTypes.string,
  hoverRadius: PropTypes.number,
  axisDropStroke: PropTypes.string,
  axisDropStrokeWidth: PropTypes.number,
}

Points.defaultProps = {
  radius: 4,
  stroke: null,
  strokeWidth: 0,
  fill: '#AAA',
  hoverRadius: null,
  axisDropStroke: '#666',
  axisDropStrokeWidth: 1,
}

// TODO: memoize
export default Points
