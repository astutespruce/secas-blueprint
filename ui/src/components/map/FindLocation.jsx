import React, {
  useCallback,
  useState,
  useEffect,
  useLayoutEffect,
  useRef,
} from 'react'
import { CaretRight, CaretDown } from '@emotion-icons/fa-solid'
import { Box, Flex } from 'theme-ui'

import { Search, LatLon } from 'components/search'
import { hasWindow } from 'util/dom'

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

  const [{ showOptions, showPlacenameResults, mode, isFocused }, setState] =
    useState({
      showOptions: false,
      showPlacenameResults: true,
      mode: 'placename',
      isFocused: false,
    })

  const toggleShowOptions = useCallback((e) => {
    e.stopPropagation()

    setState(({ showOptions: prevShowOptions, ...prevState }) => ({
      ...prevState,
      showOptions: !prevShowOptions,
      showPlacenameResults: false,
      isFocused: true,
    }))
  }, [])

  const handlePlacenameSelect = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      showPlacenameResults: false,
      isFocused: false,
    }))
  }, [])

  const handlePlacenameFocus = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      showOptions: false,
      showPlacenameResults: true,
      isFocused: true,
    }))
  }, [])

  const handleLatLonFocus = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      showOptions: false,
      isFocused: true,
    }))
  }, [])

  const setPlacenameMode = useCallback((e) => {
    e.stopPropagation()

    if (placenameInputRef.current) {
      placenameInputRef.current.focus()
    }

    setState(({ mode: prevMode, ...prevState }) => ({
      ...prevState,
      mode: 'placename',
      showOptions: false,
      showPlacenameResults: true,
      isFocused: true,
    }))
  }, [])

  const setLatLonMode = useCallback((e) => {
    e.stopPropagation()

    if (latLonInputRef.current) {
      latLonInputRef.current.focus()
    }

    setState((prevState) => ({
      ...prevState,
      mode: 'latlon',
      showOptions: false,
      isFocused: true,
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

  // prevent click from calling window click handler
  const handleClick = useCallback((e) => e.stopPropagation(), [])

  // add event listener to the window
  useEffect(() => {
    const handleWindowClick = () => {
      if (isFocused) {
        setState((prevState) => ({
          ...prevState,
          showOptions: false,
          showPlacenameResults: false,
          isFocused: false,
        }))
      }
    }

    if (hasWindow) {
      document.addEventListener('click', handleWindowClick)
    }

    return () => {
      if (hasWindow) {
        document.removeEventListener('click', handleWindowClick)
      }
    }
  }, [isFocused])

  return (
    <>
      <Box
        onClick={handleClick}
        sx={{
          ...controlCSS,
          zIndex: 2001,
          top: '10px',
          right: '10px',
          overflow: 'hidden',
          userSelect: 'none',
          width: isFocused || showOptions ? '290px' : '160px',
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
              <LatLon
                ref={latLonInputRef}
                isCompact={!isFocused}
                onFocus={handleLatLonFocus}
              />
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
