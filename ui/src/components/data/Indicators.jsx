import { graphql, useStaticQuery } from 'gatsby'

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
            id: jsonId
            label
            url
            description
            goodThreshold
            values {
              value
              label
              color
            }
            valueLabel
            subregions
          }
        }
      }
    }
  `)
  return {
    ecosystems: extractNodes(ecosystems),
    indicators: extractNodes(indicators).map(({ subregions, ...rest }, i) => ({
      ...rest,
      subregions: new Set(subregions),
      pos: i, // position within list of indicators, used to unpack packed indicator values
    })),
  }
}
