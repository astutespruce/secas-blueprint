import { graphql, useStaticQuery } from 'gatsby'

import { sortByFunc } from 'util/data'
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

  const corridors = extractNodes(rawCorridors)

  const tmp = corridors.slice().sort(sortByFunc('value'))
  const inlandCorridors = tmp
    .slice(0, 3)
    .map(({ value, ...rest }, i) => ({ value: i, ...rest }))
  const marineCorridors = tmp
    .slice(0, 1)
    .concat(tmp.slice(3, 5))
    .map(({ value, ...rest }, i) => ({ value: i, ...rest }))

  // set color for not a hub / corridor
  // NOTE: this is value 0, but in index 4
  corridors[4] = { ...corridors[4], color: '#ffebc2' }

  return {
    corridors,
    inlandCorridors,
    marineCorridors,
  }
}
