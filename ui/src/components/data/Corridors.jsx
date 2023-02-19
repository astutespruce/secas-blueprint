import { graphql, useStaticQuery } from 'gatsby'

import { extractNodes } from 'util/graphql'

/**
 * Provides corridors data in ascending order
 */
export const useCorridors = () => {
  const { corridors: rawCorridors } = useStaticQuery(graphql`
    query {
      corridors: allCorridorsJson(sort: { order: ASC }) {
        edges {
          node {
            value
            label
            color
            description
          }
        }
      }
    }
  `)

  return extractNodes(rawCorridors)
}
