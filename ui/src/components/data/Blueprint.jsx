import { useStaticQuery, graphql } from 'gatsby'

import { extractNodes } from 'util/graphql'

/**
 * Provides Blueprint priority categories in decreasing priority order
 */
export const useBlueprintPriorities = () => {
  const query = useStaticQuery(graphql`
    query {
      allBlueprintJson(sort: { fields: value, order: DESC }) {
        edges {
          node {
            color
            label
            shortLabel
            labelColor
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
    priorities: all.slice(0, all.length - 1),
  }
}
