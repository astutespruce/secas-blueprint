import { useStaticQuery, graphql } from 'gatsby'

import { indexBy } from 'util/data'
import { extractNodes } from 'util/graphql'

export const useInputAreas = () => {
  const { inputAreas, inputValues } = useStaticQuery(graphql`
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
            cpaURL
            viewerURL
            viewerName
            indicatorDescription
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
      inputValues: allInputAreaValuesJson(sort: { fields: value, order: ASC }) {
        edges {
          node {
            id: jsonId
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

  const carColors = {
    0: '#bdbdbd',
    1: '#807dba',
    2: '#005a32',
  }

  const carBlueprintLabel = {
    0: 'Not a priority',
    1: 'Medium priority',
    2: 'High priority',
  }

  // TODO: label by where it falls in blueprint
  for (let i = 1; i <= inputs.car.domain[0]; i += 1) {
    let blueprint = 0
    if (i <= 8) {
      blueprint = 2
    } else if (blueprint <= 12) {
      blueprint = 1
    }
    inputs.car.values.push({
      value: i,
      label: `${i}: ${carBlueprintLabel[blueprint]}`,
      color: carColors[blueprint],
      blueprint,
    })
  }

  return {
    inputs,
    // value is position in array
    values: extractNodes(inputValues).map(({ id }) => id),
  }
}
