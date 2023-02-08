import React, {
  useState,
  useCallback,
  useContext,
  createContext,
  useMemo,
} from 'react'
import PropTypes from 'prop-types'

import { useIndicators } from 'components/data/Indicators'

const Context = createContext()

export const Provider = ({ children }) => {
  const {
    indicators: {
      // base is only input with indicators
      base: { indicators },
    },
  } = useIndicators()

  const [{ mapMode, data, selectedIndicator, renderLayer, filters }, setState] =
    useState(() => {
      const initFilters = indicators.reduce(
        (prev, { id, values }) => ({
          ...prev,
          [id]: {
            enabled: false,
            range: [
              values[0].color === null ? values[1].value : values[0].value,
              values[values.length - 1].value,
            ],
          },
        }),
        {}
      )

      initFilters.blueprint = {
        enabled: false,
        // skip not a priority class
        range: [1, 4],
      }

      initFilters.inland_corridors = {
        enabled: false,
        range: [1, 2],
      }
      initFilters.marine_corridors = {
        enabled: false,
        range: [1, 2],
      }

      initFilters.urban = {
        enabled: false,
        range: [1, 5],
      }

      initFilters.slr = {
        enabled: false,
        // hardcoded values to capture depth + nodata
        range: [0, 13],
      }

      return {
        mapMode: 'unit', // filter, pixel, or unit
        data: null,
        selectedIndicator: null,
        renderLayer: null,
        filters: initFilters,
      }
    })

  const setData = useCallback(
    (newData) => {
      if (newData === null) {
        setState((prevState) => ({
          ...prevState,
          data: null,
          selectedIndicator: null,
        }))
        return
      }

      setState((prevState) => ({
        ...prevState,
        data: newData,
      }))
    },
    // intentionally ignores dependencies, doesn't change after mount
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  const filterRanges = useMemo(
    () =>
      Object.entries(filters).reduce(
        (prev, [id, { range }]) => ({ ...prev, [id]: range }),
        {}
      ),
    // intentionally ignores dependencies, doesn't change after mount
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  const unsetData = useCallback(() => {
    setData(null)
  }, [setData])

  const setMapMode = useCallback((mode) => {
    setState((prevState) => ({
      ...prevState,
      mapMode: mode,
      data: null,
      selectedIndicator: null,
    }))
  }, [])

  const setSelectedIndicator = useCallback((newSelectedIndicator) => {
    setState((prevState) => ({
      ...prevState,
      selectedIndicator: newSelectedIndicator,
    }))
  }, [])

  // renderLayer is null or an object: {id, label, colors, categories}
  // id is  the id in pixelLayers.js encoding for that layer
  // pass null to reset to Blueprint
  const setRenderLayer = useCallback((newRenderLayer) => {
    setState((prevState) => ({
      ...prevState,
      renderLayer: newRenderLayer,
    }))
  }, [])

  const setFilters = useCallback(({ id, enabled, range }) => {
    setState(({ filters: prevFilters, ...prevState }) => ({
      ...prevState,
      filters: {
        ...prevFilters,
        [id]: {
          enabled,
          range,
        },
      },
    }))
  }, [])

  const resetFilters = useCallback(
    () => {
      setState(({ filters: prevFilters, ...prevState }) => ({
        ...prevState,
        filters: Object.keys(prevFilters).reduce(
          (prev, id) => ({
            ...prev,
            [id]: { enabled: false, range: filterRanges[id] },
          }),
          {}
        ),
      }))
    },
    // intentionally ignores dependencies, doesn't change after mount
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  const providerValue = useMemo(
    () => ({
      data,
      setData,
      unsetData,
      mapMode,
      setMapMode,
      selectedIndicator,
      setSelectedIndicator,
      renderLayer,
      setRenderLayer,
      filters,
      setFilters,
      resetFilters,
    }),
    // other deps do not change
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [data, mapMode, selectedIndicator, renderLayer, filters]
  )

  return <Context.Provider value={providerValue}>{children}</Context.Provider>
}

Provider.propTypes = {
  children: PropTypes.node.isRequired,
}

export const useMapData = () => useContext(Context)
