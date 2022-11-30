import React, {
  createContext,
  useContext,
  useState,
  useMemo,
  useCallback,
} from 'react'
import PropTypes from 'prop-types'
import { useQuery } from 'react-query'

import { searchPlaces } from './mapbox'

const Context = createContext()

export const Provider = ({ children }) => {
  const [{ query, location }, setState] = useState({
    query: '',
    location: null,
  })

  const setQuery = useCallback((newQuery) => {
    setState((prevState) => ({ ...prevState, query: newQuery, location: null }))
  }, [])

  const setLocation = useCallback((newLocation) => {
    setState((prevState) => ({ ...prevState, location: newLocation }))
  }, [])

  const providerValue = useMemo(
    () => ({ query, setQuery, location, setLocation }),
    // other deps do not change
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [query, location]
  )

  return <Context.Provider value={providerValue}>{children}</Context.Provider>
}

Provider.propTypes = {
  children: PropTypes.node.isRequired,
}

export const useSearch = () => {
  const { query, setQuery, location, setLocation } = useContext(Context)

  const {
    isLoading,
    error,
    data: results = [],
  } = useQuery(
    ['search', query],
    () => {
      if (!query) {
        return null
      }

      return searchPlaces(query)
    },
    {
      enabled: !!query && query.length >= 3,
      staleTime: 60 * 60 * 1000, // 60 minutes
      // staleTime: 1, // use then reload to force refresh of underlying data during dev
      refetchOnWindowFocus: false,
      refetchOnMount: false,
    }
  )

  // Just log the error, there isn't much we can show the user here
  if (error) {
    // eslint-disable-next-line no-console
    console.error('ERROR loading search API results', error)
  }

  return {
    query,
    setQuery,
    location,
    setLocation,
    isLoading,
    error,
    results,
  }
}
