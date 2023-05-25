import { v4 as uuid } from 'uuid'

import { mapConfig as config } from 'components/map/mapConfig'

import { getFromStorage, saveToStorage } from 'util/dom'

import { siteMetadata } from '../../../gatsby-config'

const { mapboxToken } = siteMetadata

const apiURL = 'https://api.mapbox.com/search/searchbox/v1'
const { bounds } = config
const types = ['region', 'place', 'poi', 'address']
const numResults = 5

let sessionToken = getFromStorage('mapbox.search.session_token')
if (!sessionToken) {
  sessionToken = uuid()
  saveToStorage('mapbox.search.session_token', sessionToken)
}

export const searchPlaces = (query) => {
  const controller = new AbortController()

  const url = `${apiURL}/suggest?language=en&bbox=${bounds.toString()}&types=${types.toString()}&limit=${numResults}&access_token=${mapboxToken}&session_token=${sessionToken}&q=${encodeURI(
    query
  )}`

  const promise = fetch(url, {
    method: 'GET',
    mode: 'cors',
    signal: controller.signal,
  })
    .then((response) => {
      if (!response.ok) {
        return Promise.reject(new Error(response.statusText))
      }

      return response
        .json()
        .catch((error) =>
          Promise.reject(new Error('Invalid JSON: ', error.message))
        )
    })
    .then(({ suggestions = [] }) =>
      suggestions.map(
        ({
          mapbox_id: id,
          name,
          name_preferred: altName,
          address: rawAddress,
          full_address: fullAddress,
          place_formatted: placeFormatted,
        }) => {
          let address = fullAddress || placeFormatted
          if (placeFormatted && rawAddress && rawAddress === fullAddress) {
            address = `${fullAddress}, ${placeFormatted}`
          }
          return {
            id,
            name: altName || name,
            address,
          }
        }
      )
    )

    .catch((error) => Promise.reject(new Error(error.message)))

  promise.cancel = () => {
    controller.abort()

    // make sure to resolve promise or it raises an error on cancel
    return Promise.resolve()
  }

  return promise
}

export const getPlace = (id) => {
  const controller = new AbortController()

  const url = `${apiURL}/retrieve/${id}?access_token=${mapboxToken}&session_token=${sessionToken}`

  const promise = fetch(url, {
    method: 'GET',
    mode: 'cors',
    signal: controller.signal,
  })
    .then((response) => {
      if (!response.ok) {
        return Promise.reject(new Error(response.statusText))
      }

      return response
        .json()
        .catch((error) =>
          Promise.reject(new Error('Invalid JSON: ', error.message))
        )
    })
    .then(({ features = [] }) => {
      if (features.length === 0) {
        return null
      }

      const [
        {
          geometry: {
            coordinates: [longitude, latitude],
          },
        },
      ] = features

      return { longitude, latitude }
    })

    .catch((error) => Promise.reject(new Error(error.message)))

  promise.cancel = () => {
    controller.abort()

    // make sure to resolve promise or it raises an error on cancel
    return Promise.resolve()
  }

  return promise
}
