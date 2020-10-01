import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex } from 'theme-ui'
import { useErrorBoundary } from 'use-error-boundary'

import { Provider as SearchProvider } from 'components/search'
import { isUnsupported } from 'util/dom'
import ErrorMessage from './ErrorMessage'
import UnsupportedBrowser from './UnsupportedBrowser'
import SEO from './SEO'
import Header from './Header'
import { Provider as SelectedUnitProvider } from './SelectedUnit'
import { BreakpointProvider } from './Breakpoints'
import { siteMetadata } from '../../../gatsby-config'

const Layout = ({ children, title, overflowY }) => {
  const { ErrorBoundary, didCatch } = useErrorBoundary()

  return (
    <BreakpointProvider>
      <SelectedUnitProvider>
        <SearchProvider>
          <Flex
            sx={{
              height: '100%',
              flexDirection: 'column',
            }}
          >
            <SEO title={title || siteMetadata.title} />
            <Header />
            {isUnsupported ? (
              <UnsupportedBrowser />
            ) : (
              <Box sx={{ flex: '1 1 auto', overflowY, height: '100%' }}>
                {didCatch ? (
                  <ErrorMessage />
                ) : (
                  <ErrorBoundary>{children}</ErrorBoundary>
                )}
              </Box>
            )}
          </Flex>
        </SearchProvider>
      </SelectedUnitProvider>
    </BreakpointProvider>
  )
}

Layout.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string,
  overflowY: PropTypes.string,
}

Layout.defaultProps = {
  title: '',
  overflowY: 'auto',
}

export default Layout
