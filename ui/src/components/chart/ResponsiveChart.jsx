import React, { useRef, useLayoutEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

const ResponsiveChart = ({ children }) => {
  const node = useRef(null)
  const [{ width, height }, setState] = useState({ width: null, height: null })

  // layout effect is used to know when we have loaded, so we
  // can set the SVG based on the container height
  useLayoutEffect(() => {
    const { clientWidth, clientHeight } = node.current
    setState({ width: clientWidth, height: clientHeight })

    // listen on window resize
    function handleResize() {
      setState({
        width: node.current.clientWidth,
        height: node.current.clientHeight,
      })
    }
    window.addEventListener('resize', handleResize)

    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <Box ref={node} sx={{ height: '100%', width: '100%' }}>
      {width && height ? React.cloneElement(children, { width, height }) : null}
    </Box>
  )
}

ResponsiveChart.propTypes = {
  children: PropTypes.object.isRequired, // must be a singular child
}

export default ResponsiveChart
