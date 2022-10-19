import { useStaticQuery, graphql } from 'gatsby'

import { indexBy } from 'util/data'
import { extractNodes } from 'util/graphql'

export const useInputAreas = () => {
  const { inputAreas } = useStaticQuery(graphql`
    query {
      inputAreas: allInputsJson {
        edges {
          node {
            id: jsonId
            label
            shortLabel
            version
            dataURL
            infoURL
            valueField
            valueLabel
            valueCaption
            values {
              value
              label
              color
              blueprint
            }
            domain
            description
          }
        }
      }
    }
  `)
  const inputs = indexBy(extractNodes(inputAreas), 'id')

  // set color for non-priority Caribbean values
  inputs.car.values = inputs.car.values.map(({ color, ...rest }) => ({
    ...rest,
    color: color || '#ffebc2',
  }))

  return inputs
}
