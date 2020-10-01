import React from 'react'
import PropTypes from 'prop-types'

import FluidImage from './Fluid'

const Banner = ({
  src: {
    childImageSharp: { fluid: src },
  },
  credit,
  url,
  caption,
  ...props
}) => {
  const credits = credit ? { author: credit, url } : null

  return (
    <FluidImage image={src} credits={credits} caption={caption} {...props} />
  )
}

Banner.propTypes = {
  src: PropTypes.object.isRequired,
  credit: PropTypes.string,
  url: PropTypes.string,
  caption: PropTypes.string,
}

Banner.defaultProps = {
  credit: null,
  url: null,
  caption: null,
}

export default Banner
