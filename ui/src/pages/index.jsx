import React from 'react'

import { MapDataProvider } from 'components/data'
import { Layout, SEO } from 'components/layout'
import { MapContainer } from 'components/map'

const IndexPage = () => (
  <MapDataProvider>
    <Layout overflowY="hidden">
      <MapContainer />
    </Layout>
  </MapDataProvider>
)

export default IndexPage

export const Head = () => <SEO />
