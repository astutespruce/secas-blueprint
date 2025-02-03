import React, {
  useState,
  useCallback,
  useContext,
  createContext,
  useMemo,
} from 'react'
import PropTypes from 'prop-types'

import { indicators, ownership, protection } from 'config'
import { indexBy, range } from 'util/data'
import { logGAEvent } from 'util/log'
import { renderLayersIndex } from 'components/map/pixelLayers'

const Context = createContext()

export const Provider = ({ children }) => {
  const [
    {
      mapMode,
      data,
      selectedIndicator,
      renderLayer,
      filters,
      visibleSubregions, // only set when in filter mode
    },
    setState,
  ] = useState(() => {
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
      // values 1-6
      activeValues: Object.fromEntries(range(1, 7).map((v) => [v, true])),
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

    initFilters.wildfireRisk = {
      enabled: false,
      // values 0-10
      activeValues: Object.fromEntries(range(0, 11).map((v) => [v, true])),
    }

    initFilters.ownership = {
      enabled: false,
      // all values excluding areas outside protected areas (0)
      activeValues: Object.fromEntries(
        range(1, ownership[ownership.length - 1].code + 1).map((v) => [v, true])
      ),
    }

    initFilters.protection = {
      enabled: false,
      // all values
      activeValues: Object.fromEntries(
        range(1, protection[protection.length - 1].code + 1).map((v) => [
          v,
          true,
        ])
      ),
    }

    return {
      mapMode: 'unit', // filter, pixel, or unit
      data: null,
      selectedIndicator: null,
      renderLayer: renderLayersIndex.blueprint,
      filters: initFilters,
      visibleSubregions: new Set(),
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

      if (newData.type !== 'pixel') {
        logGAEvent('set-map-data', {
          type: newData.type,
          id: `${newData.type}:${newData.id}`,
        })
      }
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

    if (newSelectedIndicator) {
      logGAEvent('show-indicator-details', {
        indicator: newSelectedIndicator,
      })
    }
  }, [])

  // renderLayer is an object: {id, label, colors, categories}
  // id is  the id in pixelLayers.js encoding for that layer
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

  const setVisibleSubregions = useCallback((newVisibleSubregions) => {
    setState((prevState) => ({
      ...prevState,
      visibleSubregions: newVisibleSubregions,
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
      visibleSubregions,
      setVisibleSubregions,
    }),
    // other deps do not change
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [data, mapMode, selectedIndicator, renderLayer, filters, visibleSubregions]
  )

  return <Context.Provider value={providerValue}>{children}</Context.Provider>
}

Provider.propTypes = {
  children: PropTypes.node.isRequired,
}

export const useMapData = () => useContext(Context)
