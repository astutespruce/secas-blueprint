import React from 'react'
import PropTypes from 'prop-types'
import { line } from 'd3-shape'

const Line = ({ points, stroke, strokeWidth }) => {
  const path = line()(points.map(({ x, y }) => [x, y]))

  return <path d={path} fill="none" stroke={stroke} strokeWidth={strokeWidth} />
}

Line.propTypes = {
  points: PropTypes.arrayOf(
    PropTypes.shape({
      x: PropTypes.number.isRequired,
      y: PropTypes.number.isRequired,
    })
  ).isRequired,
  stroke: PropTypes.string,
  strokeWidth: PropTypes.number,
}

Line.defaultProps = {
  stroke: '#AAA',
  strokeWidth: 1,
}

export default Line
