import { graphql, useStaticQuery } from 'gatsby'
import { extractNodes } from 'util/graphql'

export const useIndicators = () => {
  const { ecosystems } = useStaticQuery(graphql`
    query {
      ecosystems: allEcosystemsJson {
        edges {
          node {
            id
            label
            color
            borderColor
            # indicators
          }
        }
      }
    }
  `)

  return {
    ecosystems: extractNodes(ecosystems),
  }
}
