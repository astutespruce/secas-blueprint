import React, { useState, useCallback, useContext, createContext } from 'react'
import PropTypes from 'prop-types'

const Context = createContext()

export const Provider = ({ children }) => {
  const [{ mapMode, data, selectedIndicator }, setState] = useState({
    mapMode: 'unit', // pixel or unit
    data: null,
    selectedIndicator: null,
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
