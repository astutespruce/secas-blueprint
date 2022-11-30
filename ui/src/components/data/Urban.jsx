import { graphql, useStaticQuery } from 'gatsby'

import { extractNodes } from 'util/graphql'

/**
 * Provides urban categories in order intended to appear
 */
export const useUrban = () => {
  const { urban: rawUrban } = useStaticQuery(graphql`
    query {
      urban: allUrbanJson {
        edges {
          node {
            value
            label
            color
          }
        }
      }
    }
  `)

  return extractNodes(rawUrban)
}
