import { graphql, useStaticQuery } from 'gatsby'

import { indexBy } from 'util/data'
import { extractNodes } from 'util/graphql'

export const useIndicators = () => {
  const { ecosystems, indicators } = useStaticQuery(graphql`
    query {
      ecosystems: allEcosystemsJson {
        edges {
          node {
            id: jsonId
            label
            color
            borderColor
            indicators
          }
        }
      }
      indicators: allIndicatorsJson {
        edges {
          node {
            input
            indicators {
              id # note: not jsonId here due to embedded structure
              label
              url
              description
              goodThreshold
              values {
                value
                label
              }
            }
          }
        }
      }
    }
  `)
  return {
    ecosystems: extractNodes(ecosystems),
    indicators: indexBy(extractNodes(indicators), 'input'),
  }
}
