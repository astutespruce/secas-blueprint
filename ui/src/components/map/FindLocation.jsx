import React, { useCallback, useState, useLayoutEffect, useRef } from 'react'
import { CaretRight, CaretDown } from '@emotion-icons/fa-solid'
import { Box, Flex } from 'theme-ui'

import { Search, LatLon } from 'components/search'

const controlCSS = {
  alignItems: 'center',
  justifyContent: 'center',
  position: 'absolute',
  padding: '6px',
  color: 'grey.9',
  bg: '#FFF',
  pointerEvents: 'auto',
  borderRadius: '0.25rem',
  boxShadow: '0 0 0 2px rgba(0,0,0,.1)',
}

const FindLocation = () => {
  const placenameInputRef = useRef()
  const latLonInputRef = useRef(null)
  const isMountedRef = useRef(false)

  const [{ showOptions, showPlacenameResults, mode }, setState] = useState({
    showOptions: false,
    showPlacenameResults: true,
    mode: 'placename',
  })

  const toggleShowOptions = useCallback(() => {
    setState(({ showOptions: prevShowOptions, ...prevState }) => ({
      ...prevState,
      showOptions: !prevShowOptions,
      showPlacenameResults: false,
    }))
  }, [])

  const handlePlacenameSelect = useCallback(() => {
    setState((prevState) => ({ ...prevState, showPlacenameResults: false }))
  }, [])

  const handlePlacenameFocus = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      showOptions: false,
      showPlacenameResults: true,
    }))
  }, [])

  const handleLatLonFocus = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      showOptions: false,
    }))
  }, [])

  const setPlacenameMode = useCallback(() => {
    setState(({ mode: prevMode, ...prevState }) => ({
      ...prevState,
      mode: 'placename',
      showOptions: false,
      showPlacenameResults: true,
    }))
  }, [])

  const setLatLonMode = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      mode: 'latlon',
      showOptions: false,
    }))
  }, [])

  useLayoutEffect(() => {
    // skip on first mount
    if (!isMountedRef.current) {
      isMountedRef.current = true
      return
    }

    if (mode === 'placename') {
      if (placenameInputRef.current) {
        placenameInputRef.current.focus()
      }
    } else if (latLonInputRef.current) {
      latLonInputRef.current.focus()
    }
  }, [mode])

  return (
    <>
      <Box
        sx={{
          ...controlCSS,
          zIndex: 20001,
          top: '10px',
          right: '10px',
          overflow: 'hidden',
          userSelect: 'none',
          width: '290px',
        }}
      >
        <Flex sx={{ alignItems: 'flex-start' }}>
          <Box
            onClick={toggleShowOptions}
            sx={{ flex: '0 0 auto', cursor: 'pointer', color: 'grey.8' }}
          >
            {showOptions ? (
              <CaretDown size="1.5em" />
            ) : (
              <CaretRight size="1.5em" style={{ marginTop: '0.2rem' }} />
            )}
          </Box>
          <Box sx={{ flex: '1 1 auto', fontSize: 0 }}>
            <Box
              sx={{
                display: mode === 'placename' ? 'block' : 'none',
                '& .search-results': {
                  mt: '0.5rem',
                  ml: '-1.5rem',
                  display: showPlacenameResults ? 'block' : 'none',
                },
              }}
            >
              <Search
                ref={placenameInputRef}
                onFocus={handlePlacenameFocus}
                onSelect={handlePlacenameSelect}
              />
            </Box>

            <Box
              sx={{
                display: mode === 'latlon' ? 'block' : 'none',
              }}
            >
              <LatLon ref={latLonInputRef} onFocus={handleLatLonFocus} />
            </Box>
          </Box>
        </Flex>

        {showOptions ? (
          <Box
            sx={{
              mt: '0.25rem',
              pt: '0.25rem',
              borderTop: '1px solid',
              borderTopColor: 'grey.3',
              fontSize: 1,
              lineHeight: 1,
              '& > div': {
                p: '0.25rem',
                cursor: 'pointer',
                '&:hover': {
                  bg: 'grey.0',
                },
              },
            }}
          >
            <Box onClick={setPlacenameMode}>Find by a name or address</Box>
            <Box onClick={setLatLonMode}>Find by latitude & longitude</Box>
          </Box>
        ) : null}
      </Box>
    </>
  )
}

// TODO: memo?
export default FindLocation
