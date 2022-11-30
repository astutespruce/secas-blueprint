import React, {
  useState,
  useCallback,
  useContext,
  createContext,
  useMemo,
} from 'react'
import PropTypes from 'prop-types'

const Context = createContext()

export const Provider = ({ children }) => {
  const [{ mapMode, data, selectedIndicator, renderLayer }, setState] =
    useState({
      mapMode: 'unit', // pixel or unit
      data: null,
      selectedIndicator: null,
      renderLayer: null,
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
    // intentionally ignores dependencies
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  const unsetData = useCallback(() => {
    setData(null)
  }, [setData])

  const setMapMode = useCallback((mode) => {
    setState(() => ({
      mapMode: mode,
      data: null,
      selectedIndicator: null,
      renderLayer: null,
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
    }),
    // other deps do not change
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [data, mapMode, selectedIndicator, renderLayer]
  )

  return <Context.Provider value={providerValue}>{children}</Context.Provider>
}

Provider.propTypes = {
  children: PropTypes.node.isRequired,
}

export const useMapData = () => useContext(Context)
