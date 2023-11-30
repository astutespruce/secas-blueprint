import React, {
  createContext,
  useContext,
  useState,
  useMemo,
  useCallback,
} from 'react'
import PropTypes from 'prop-types'
import { useQuery } from '@tanstack/react-query'

import { logGAEvent } from 'util/log'
import { searchPlaces, getPlace } from './mapbox'

const Context = createContext()

export const Provider = ({ children }) => {
  const [{ query, selectedId, location }, setState] = useState({
    query: '',
    selectedId: null,
    location: null,
  })

  const setQuery = useCallback((newQuery) => {
    setState((prevState) => ({
      ...prevState,
      query: newQuery,
      selectedId: null,
      location: null,
    }))

    if (newQuery) {
      logGAEvent('search-place')
    }
  }, [])

  const setSelectedId = useCallback((newId) => {
    setState((prevState) => ({
      ...prevState,
      location: null,
      selectedId: newId,
    }))

    if (newId !== null) {
      logGAEvent('search-place-selected')
    }
  }, [])

  const setLocation = useCallback((newLocation) => {
    setState((prevState) => ({
      ...prevState,
      location: newLocation,
      selectedId: null,
      query: '',
    }))
  }, [])

  const reset = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      query: '',
      selectedId: null,
      location: null,
    }))
  }, [])

  const providerValue = useMemo(
    () => ({
      query,
      setQuery,
      selectedId,
      setSelectedId,
      location,
      setLocation,
      reset,
    }),
    // callbacks do not change
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [query, location, selectedId]
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
  } = useQuery({
    queryKey: ['search', query],
    queryFn: () => {
      if (!query) {
        return null
      }

      return searchPlaces(query)
    },

    enabled: !!query && query.length >= 3,
    staleTime: 60 * 60 * 1000, // 60 minutes
    // staleTime: 1, // use then reload to force refresh of underlying data during dev
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

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
  } = useQuery({
    queryKey: ['retrieve', selectedId],
    queryFn: () => {
      if (!selectedId) {
        return null
      }

      return getPlace(selectedId)
    },

    enabled: !!selectedId,
    staleTime: 60 * 60 * 1000, // 60 minutes
    // staleTime: 1, // use then reload to force refresh of underlying data during dev
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  // Just log the error, there isn't much we can show the user here
  if (error) {
    // eslint-disable-next-line no-console
    console.error('ERROR retrieving result from search API ', error)
  }

  return {
    isLoading,
    error,
    location,
  }
}

export const useSearch = () => {
  const {
    query,
    setQuery,
    selectedId,
    setSelectedId,
    location,
    setLocation,
    reset,
  } = useContext(Context)

  const {
    isLoading: suggestionLoading,
    error: suggestionError,
    results,
  } = useSearchSuggestions(query)
  const { location: searchLocation, error: retrieveError } =
    useRetriveItemDetails(selectedId)

  return {
    reset,
    query,
    setQuery,
    selectedId,
    setSelectedId,
    location: searchLocation || location,
    setLocation,
    isLoading: suggestionLoading,
    error: suggestionError || retrieveError,
    results,
  }
}
