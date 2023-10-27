import { useStaticQuery, graphql } from 'gatsby'

import { extractNodes } from 'util/graphql'

/**
 * Provides Blueprint categories in decreasing priority order
 */
export const useBlueprintPriorities = () => {
  const query = useStaticQuery(graphql`
    query {
      allBlueprintJson(sort: { value: DESC }) {
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
    // remove 0 value (lowest priority)
    categories: all.slice(0, all.length - 1),
  }
}
