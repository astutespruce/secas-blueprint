import React, {
  createContext,
  useContext,
  useState,
  useMemo,
  useCallback,
} from 'react'
import PropTypes from 'prop-types'
import { useQuery } from 'react-query'

import { searchPlaces, getPlace } from './mapbox'

const Context = createContext()

export const Provider = ({ children }) => {
  const [{ query, selectedId }, setState] = useState({
    query: '',
    selectedId: null,
  })

  const setQuery = useCallback((newQuery) => {
    setState((prevState) => ({
      ...prevState,
      query: newQuery,
      selectedId: null,
      location: null,
    }))
  }, [])

  const setSelectedId = useCallback((newId) => {
    setState((prevState) => ({
      ...prevState,
      location: null,
      selectedId: newId,
    }))
  }, [])

  const providerValue = useMemo(
    () => ({
      query,
      setQuery,
      selectedId,
      setSelectedId,
    }),
    // other deps do not change
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [query, selectedId]
  )

  return <Context.Provider value={providerValue}>{children}</Context.Provider>
}

Provider.propTypes = {
  children: PropTypes.node.isRequired,
}

const useSearchSuggestions = (query) => {
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

  return { isLoading, error, results }
}

const useRetriveItemDetails = (selectedId) => {
  const {
    isLoading,
    error,
    data: location = null,
  } = useQuery(
    ['retrieve', selectedId],
    () => {
      if (!selectedId) {
        return null
      }

      return getPlace(selectedId)
    },
    {
      enabled: !!selectedId,
      staleTime: 60 * 60 * 1000, // 60 minutes
      // staleTime: 1, // use then reload to force refresh of underlying data during dev
      refetchOnWindowFocus: false,
      refetchOnMount: false,
    }
  )

  // Just log the error, there isn't much we can show the user here
  if (error) {
    // eslint-disable-next-line no-console
    console.error('ERROR retrieving result from search API ', error)
  }

  console.log('retrieved location', location)

  return {
    isLoading,
    error,
    location,
  }
}

export const useSearch = () => {
  const { query, setQuery, selectedId, setSelectedId } = useContext(Context)

  const {
    isLoading: suggestionLoading,
    error: suggestionError,
    results,
  } = useSearchSuggestions(query)
  const { location, error: retrieveError } = useRetriveItemDetails(selectedId)

  return {
    query,
    setQuery,
    selectedId,
    setSelectedId,
    location,
    isLoading: suggestionLoading,
    error: suggestionError || retrieveError,
    results,
  }
}
