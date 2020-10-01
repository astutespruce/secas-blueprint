import React from 'react'
import PropTypes from 'prop-types'
import { area } from 'd3-shape'

const Area = ({ points, baseline, fill, fillOpacity }) => {
  const path = area()
    .x0(({ x }) => x)
    .y0(baseline)
    .y1(({ y }) => y)(points)

  return <path d={path} fill={fill} fillOpacity={fillOpacity} />
}

Area.propTypes = {
  points: PropTypes.arrayOf(
    PropTypes.shape({
      x: PropTypes.number.isRequired,
      y: PropTypes.number.isRequired,
    })
  ).isRequired,
  // baseline is the maxY value (starting from top left coordinate of SVG)
  baseline: PropTypes.number.isRequired,
  fill: PropTypes.string,
  fillOpacity: PropTypes.number,
}

Area.defaultProps = {
  fill: '#EEE',
  fillOpacity: 0.75,
}

export default Area
