import React, {
  useState,
  useCallback,
  useContext,
  createContext,
  useMemo,
} from 'react'
import PropTypes from 'prop-types'

import { useIndicators } from 'components/data/Indicators'
import { useBlueprintPriorities } from 'components/data/Blueprint'
import { useCorridors } from 'components/data/Corridors'

const Context = createContext()

export const Provider = ({ children }) => {
  const { all: blueprint } = useBlueprintPriorities()
  const corridors = useCorridors()
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
            // set to full range by default, so there is no change when filter
            // is first enabled
            range: [values[0].value, values[values.length - 1].value],
          },
        }),
        {}
      )

      initFilters.blueprint = {
        enabled: false,
        // values are in reverse order
        range: [blueprint[blueprint.length - 1].value, blueprint[0].value],
      }
      initFilters.corridors = {
        enabled: false,
        range: [corridors[0].value, corridors[corridors.length - 1].value],
      }

      initFilters.urban = {
        enabled: false,
        // hardcoded values because values are not in incremental order
        range: [0, 4],
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
