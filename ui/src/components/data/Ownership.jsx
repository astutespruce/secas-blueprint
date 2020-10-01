import { graphql, useStaticQuery } from 'gatsby'

import { extractNodes } from 'util/graphql'

/**
 * Provides ownership and protection levels
 */
export const useOwnership = () => {
  const { ownership, protection } = useStaticQuery(graphql`
    query {
      ownership: allOwnershipJson {
        edges {
          node {
            id: value
            label
            color
          }
        }
      }
      protection: allProtectionJson {
        edges {
          node {
            id: value
            label
            color
          }
        }
      }
    }
  `)

  return {
    ownership: extractNodes(ownership),
    protection: extractNodes(protection),
  }
}
