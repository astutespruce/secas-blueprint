import React, { useState, useCallback, useContext, createContext } from 'react'
import PropTypes from 'prop-types'

const Context = createContext()

export const Provider = ({ children }) => {
  const [{ mapMode, data }, setState] = useState({
    mapMode: 'unit', // TODO: pixel, once supported
    data: null,
  })

  const setData = useCallback((newData) => {
    setState((prevState) => ({
      ...prevState,
      data: newData,
    }))
  }, [])

  const unsetData = useCallback(() => {
    setData(null)
  }, [setData])

  const setMapMode = useCallback((mode) => {
    setState(() => ({
      mapMode: mode,
      data: null,
    }))
  }, [])

  return (
    <Context.Provider value={{ data, setData, unsetData, mapMode, setMapMode }}>
      {children}
    </Context.Provider>
  )
}

Provider.propTypes = {
  children: PropTypes.node.isRequired,
}

export const useMapData = () => useContext(Context)
