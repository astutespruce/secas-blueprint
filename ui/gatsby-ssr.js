import React from 'react'
import { QueryClient, QueryClientProvider } from 'react-query'
import { withPrefix } from 'gatsby'

const queryClient = new QueryClient()

export const wrapRootElement = ({ element }) => (
  <QueryClientProvider client={queryClient}>{element}</QueryClientProvider>
)

// preload fonts so there is no flash of unstyled fonts
const fonts = [
  'source-sans-pro-400.woff2',
  'source-sans-pro-700.woff2',
  'source-sans-pro-900.woff2',
]

export const onRenderBody = ({ setHeadComponents }) => {
  setHeadComponents(
    fonts.map((font) => {
      const url = withPrefix(`/fonts/${font}`)
      return (
        <link
          key={font}
          as="font"
          href={url}
          rel="preload"
          crossOrigin="anonymous"
        />
      )
    })
  )
}
