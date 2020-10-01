import React, { useContext, createContext } from 'react'
import PropTypes from 'prop-types'
import theme from 'gatsby-plugin-theme-ui'
import { hasWindow } from 'util/dom'

const breakpoints = theme.breakpoints.map((b) =>
  parseInt(b.replace('px', ''), 10)
)

const getBreakpoint = () => {
  // make sure build uses desktop version
  if (!hasWindow) return breakpoints.length - 1

  const { innerWidth } = window

  if (innerWidth > breakpoints[breakpoints.length - 1]) {
    return breakpoints.length - 1
  }

  for (let i = 0; i < breakpoints.length; i += 1) {
    if (innerWidth <= breakpoints[i]) {
      return i
    }
  }

  return breakpoints.length - 1
}

const context = createContext({})

export const BreakpointProvider = ({ children }) => {
  const [breakpoint, setBreakpoint] = React.useState(() => getBreakpoint())

  const handleWindowResize = () => {
    setBreakpoint(getBreakpoint)
  }

  React.useEffect(() => {
    window.addEventListener('resize', handleWindowResize)
    return () => window.removeEventListener('resize', handleWindowResize)
  }, [])

  return <context.Provider value={breakpoint}>{children}</context.Provider>
}

BreakpointProvider.propTypes = {
  children: PropTypes.node.isRequired,
}

export const useBreakpoints = () => {
  return useContext(context)
}
