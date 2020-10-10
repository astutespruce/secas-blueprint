import { useStaticQuery, graphql } from 'gatsby'

import { indexBy } from 'util/data'
import { extractNodes } from 'util/graphql'

export const useInputAreas = () => {
  const { inputAreas, inputValues } = useStaticQuery(graphql`
    query {
      inputAreas: allInputsJson {
        edges {
          node {
            id
            label
            version
            dataURL
            infoURL
            viewerURL
            viewerName
            valueField
            valueLabel
            values {
              value
              label
              color
            }
          }
        }
      }
      inputValues: allInputAreaValuesJson(sort: { fields: value, order: ASC }) {
        edges {
          node {
            id
          }
        }
      }
    }
  `)

  return {
    inputs: indexBy(extractNodes(inputAreas), 'id'),
    // value is position in array
    values: extractNodes(inputValues).map(({ id }) => id),
  }
}
