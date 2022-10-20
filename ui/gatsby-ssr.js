import React from 'react'
import { QueryClient, QueryClientProvider } from 'react-query'

const queryClient = new QueryClient()

export const wrapRootElement = ({ element }) => (
  <QueryClientProvider client={queryClient}>{element}</QueryClientProvider>
)

export const onRenderBody = ({ setHtmlAttributes }) => {
  setHtmlAttributes({ lang: 'en' })
}
