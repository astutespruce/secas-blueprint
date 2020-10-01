import { useStaticQuery, graphql } from 'gatsby'

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
  `).allBlueprintJson

  const inputs = extractNodes(inputAreas)

  // value is position in array
  const values = extractNodes(inputValues).map(({ id }) => id)

  return {
    inputs,
    values,
  }
}
