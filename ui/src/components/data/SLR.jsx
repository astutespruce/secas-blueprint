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
          }
        }
      }
    }
  `)

  const slr = extractNodes(rawSLR)

  return {
    depth: slr.slice(0, 11),
    nodata: slr.slice(11),
  }
}
