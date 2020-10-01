import React, { useState, useCallback, useContext, createContext } from 'react'
import PropTypes from 'prop-types'

const Context = createContext()

export const Provider = ({ children }) => {
  const [selectedUnit, selectUnit] = useState(null)

  const deselectUnit = useCallback(() => selectUnit(null), [])

  return (
    <Context.Provider value={{ selectedUnit, selectUnit, deselectUnit }}>
      {children}
    </Context.Provider>
  )
}

Provider.propTypes = {
  children: PropTypes.node.isRequired,
}

export const useSelectedUnit = () => {
  return useContext(Context)
}
