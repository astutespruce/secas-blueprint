import { graphql, useStaticQuery } from 'gatsby'

import { extractNodes } from 'util/graphql'

/**
 * Provides corridors data in ascending order
 */
export const useCorridors = () => {
  const { corridors: rawCorridors } = useStaticQuery(graphql`
    query {
      corridors: allCorridorsJson(sort: { value: ASC }) {
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

  const corridors = extractNodes(rawCorridors)

  // set color for not a hub / corridor
  corridors[4].color = '#ffebc2'

  return corridors
}
