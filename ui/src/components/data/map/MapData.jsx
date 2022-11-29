import React, { useState, useCallback, useContext, createContext } from 'react'
import PropTypes from 'prop-types'

import { useIndicators } from 'components/data/Indicators'
import { unpackFeatureData } from './features'

const Context = createContext()

export const Provider = ({ children }) => {
  const { ecosystems: ecosystemInfo, indicators: indicatorInfo } =
    useIndicators()

  const [{ mapMode, data, selectedIndicator }, setState] = useState({
    mapMode: 'pixel', // 'unit', // pixel or unit
    data: null,
    selectedIndicator: null,
  })

  const setData = useCallback(
    (rawData) => {
      if (rawData === null) {
        setState((prevState) => ({
          ...prevState,
          data: null,
          selectedIndicator: null,
        }))
        return
      }

      let newData = rawData
      if (mapMode === 'unit') {
        newData = unpackFeatureData(rawData, ecosystemInfo, indicatorInfo)
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
    }))
  }, [])

  const setSelectedIndicator = useCallback((newSelectedIndicator) => {
    setState((prevState) => ({
      ...prevState,
      selectedIndicator: newSelectedIndicator,
    }))
  }, [])

  return (
    <Context.Provider
      value={{
        data,
        setData,
        unsetData,
        mapMode,
        setMapMode,
        selectedIndicator,
        setSelectedIndicator,
      }}
    >
      {children}
    </Context.Provider>
  )
}

Provider.propTypes = {
  children: PropTypes.node.isRequired,
}

export const useMapData = () => useContext(Context)
