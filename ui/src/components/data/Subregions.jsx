import { graphql, useStaticQuery } from 'gatsby'

import { indexBy } from 'util/data'
import { extractNodes } from 'util/graphql'

export const useSubregions = () => {
  const { subregions: rawSubregions } = useStaticQuery(graphql`
    query {
      subregions: allSubregionsJson {
        edges {
          node {
            value
            subregion
            marine
          }
        }
      }
    }
  `)

  const subregions = extractNodes(rawSubregions)

  return {
    subregions,
    subregionIndex: indexBy(subregions, 'value'),
  }
}
