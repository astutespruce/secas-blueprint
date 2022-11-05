import { useStaticQuery, graphql } from 'gatsby'

import { extractNodes } from 'util/graphql'

/**
 * Provides Blueprint categories in decreasing priority order
 */
export const useBlueprintPriorities = () => {
  const query = useStaticQuery(graphql`
    query {
      allBlueprintJson(sort: { fields: value, order: DESC }) {
        edges {
          node {
            value
            color
            label
            shortLabel
            percent
            description
          }
        }
      }
    }
  `).allBlueprintJson

  const all = extractNodes(query)

  return {
    all,
    categories: all.slice(0, all.length - 1),
  }
}
