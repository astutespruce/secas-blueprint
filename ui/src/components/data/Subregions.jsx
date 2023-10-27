import { graphql, useStaticQuery } from 'gatsby'

import { extractNodes } from 'util/graphql'

export const useSubregions = () => {
  const { subregions } = useStaticQuery(graphql`
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

  return extractNodes(subregions)
}
