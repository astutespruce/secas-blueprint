import { graphql, useStaticQuery } from 'gatsby'

import { extractNodes } from 'util/graphql'

export const useCorridors = () => {
  const { corridors: rawCorridors } = useStaticQuery(graphql`
    query {
      corridors: allCorridorsJson {
        edges {
          node {
            value
            label
            color
            description
            type
          }
        }
      }
    }
  `)

  const corridors = extractNodes(rawCorridors)

  // put 0 value at end
  return corridors.slice(1).concat(corridors.slice(0, 1))
}
