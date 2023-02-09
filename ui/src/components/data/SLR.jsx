import { graphql, useStaticQuery } from 'gatsby'

import { extractNodes } from 'util/graphql'

/**
 * Provides SLR categories in order intended to appear
 */
export const useSLR = () => {
  const { slr: rawSLR } = useStaticQuery(graphql`
    query {
      slr: allSlrJson {
        edges {
          node {
            value
            label
            color
          }
        }
      }
    }
  `)

  const slr = extractNodes(rawSLR)

  return {
    depth: slr.slice(0, 11),
    nodata: slr.slice(11).map(({ color, value, ...rest }) => ({
      ...rest,
      value,
      // make not modeled class white since we add crosshatches
      color: value === 13 ? '#FFFFFF' : color,
    })),
  }
}
