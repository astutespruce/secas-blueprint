import React, {
  useState,
  useCallback,
  useContext,
  createContext,
  useMemo,
} from 'react'
import PropTypes from 'prop-types'

import { useIndicators } from 'components/data/Indicators'
import { indexBy, range } from 'util/data'

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
      const initFilters = indicators.reduce((prev, { id, values }) => {
        const valuesIndex = indexBy(values, 'value')

        return {
          ...prev,
          [id]: {
            enabled: false,
            activeValues: Object.fromEntries(
              range(values[0].value, values[values.length - 1].value + 1).map(
                (v) => [
                  v,
                  // disable value if we don't normally show it
                  valuesIndex[v] && valuesIndex[v].color !== null,
                ]
              )
            ),
          },
        }
      }, {})

      initFilters.blueprint = {
        enabled: false,
        // skip not a priority class; values 1-4
        activeValues: Object.fromEntries(range(1, 5).map((v) => [v, true])),
      }

      initFilters.corridors = {
        enabled: false,
        // values 1-4
        activeValues: Object.fromEntries(range(1, 5).map((v) => [v, true])),
      }

      initFilters.urban = {
        enabled: false,
        // values 1-5
        activeValues: Object.fromEntries(range(1, 6).map((v) => [v, true])),
      }

      initFilters.slr = {
        enabled: false,
        // hardcoded values to capture depth + nodata (values 0-13)
        activeValues: Object.fromEntries(range(0, 14).map((v) => [v, true])),
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

  // save initial activeValues for reset
  const initFilterValues = useMemo(
    () =>
      Object.entries(filters).reduce(
        (prev, [id, { activeValues }]) => ({ ...prev, [id]: activeValues }),
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

  const setFilters = useCallback(({ id, enabled, activeValues }) => {
    setState(({ filters: prevFilters, ...prevState }) => ({
      ...prevState,
      filters: {
        ...prevFilters,
        [id]: {
          enabled,
          activeValues,
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
            [id]: { enabled: false, activeValues: initFilterValues[id] },
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
