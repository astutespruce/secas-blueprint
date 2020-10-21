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
            valueCaption
            values {
              value
              label
              color
            }
            domain
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

  const inputs = indexBy(extractNodes(inputAreas), 'id')

  // programmatically generate values for Caribbean
  inputs.car.values = [
    {
      value: 0,
      label: 'Not a priority',
      color: '#EEE',
    },
  ]
  for (let i = 1; i <= inputs.car.domain[0]; i += 1) {
    inputs.car.values.push({
      value: i,
      label: i,
      color: 'red', // TODO
    })
  }

  return {
    inputs,
    // value is position in array
    values: extractNodes(inputValues).map(({ id }) => id),
  }
}
