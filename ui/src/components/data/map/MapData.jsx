import React, { useState, useCallback, useContext, createContext } from 'react'
import PropTypes from 'prop-types'

import { useInputAreas } from 'components/data/InputAreas'
import { useIndicators } from 'components/data/Indicators'
import { unpackFeatureData } from './features'

const Context = createContext()

export const Provider = ({ children }) => {
  const { values: inputValues, inputs: inputInfo } = useInputAreas()
  const {
    ecosystems: ecosystemInfo,
    indicators: indicatorInfo,
  } = useIndicators()

  const [{ mapMode, data, selectedIndicator }, setState] = useState({
    mapMode: 'unit', // TODO: pixel, once supported
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

      // transform map data
      const newData = unpackFeatureData(
        rawData,
        inputValues,
        inputInfo,
        ecosystemInfo,
        indicatorInfo
      )
      console.log('transformed feature data', newData)

      // TODO: if a different input area than indicator, set it to null

      setState((prevState) => ({
        ...prevState,
        data: newData,
      }))
    },
    // intentionally ignores dependencies
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
