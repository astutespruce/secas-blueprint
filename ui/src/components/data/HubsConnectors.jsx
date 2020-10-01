import { graphql, useStaticQuery } from 'gatsby'

import { extractNodes } from 'util/graphql'

/**
 * Provides hubs and connectors data in ascending order
 */
export const useHubsConnectors = () => {
  const { hubsConnectors } = useStaticQuery(graphql`
    query {
      hubsConnectors: allHubsConnectorsJson(
        sort: { fields: value, order: ASC }
      ) {
        edges {
          node {
            label
            color
          }
        }
      }
    }
  `)

  return extractNodes(hubsConnectors)
}
