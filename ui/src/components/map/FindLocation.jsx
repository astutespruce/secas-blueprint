import React, { useState, useCallback } from 'react'
import {
  LocationArrow,
  SearchLocation,
  TimesCircle,
  TrashAlt,
} from '@emotion-icons/fa-solid'
import { Box, Button, Grid, Input, Flex, Spinner, Text } from 'theme-ui'

import { Search, useSearch } from 'components/search'
import { Tabs } from 'components/tabs'
import { hasGeolocation } from 'util/dom'

const navigatorOptions = {
  enableHighAccuracy: false,
  maximumAge: 0,
  timeout: 6000,
}

const controlCSS = {
  alignItems: 'center',
  justifyContent: 'center',
  position: 'absolute',

  padding: '6px',
  color: 'grey.9',
  bg: '#FFF',
  pointerEvents: 'auto',
  borderRadius: '0.25rem',
  boxShadow: '2px 2px 6px #333',
}

const inputCSS = {
  flex: '0 0 auto',
  width: '132px',
  fontSize: 0,
  borderRadius: '0.25rem',
  outline: 'none',
  py: '0.25rem',
  px: '0.5rem',
}
const invalidInputCSS = {
  ...inputCSS,
  borderWidth: '1px 0.5rem 1px 1px',
  borderStyle: 'solid',
  borderColor: 'accent',
}

const tabs = [
  {
    id: 'find',
    label: 'Search by name',
  },
  { id: 'latlong', label: 'Go to lat/long' },
]

const FindLocation = () => {
  const [
    { isOpen, isPending, tab, lat, lon, isLatValid, isLonValid },
    setState,
  ] = useState({
    isOpen: true, // FIXME: false,
    isPending: false,
    tab: 'find',
    lat: '',
    lon: '',
    isLatValid: true,
    isLonValid: true,
  })

  const { setLocation } = useSearch()

  const handleLatitudeChange = ({ target: { value } }) => {
    setState((prevState) => ({
      ...prevState,
      lat: value,
      isLatValid: value === '' || Math.abs(parseFloat(value)) < 89,
    }))
  }

  const handleLongitudeChange = ({ target: { value } }) => {
    setState((prevState) => ({
      ...prevState,
      lon: value,
      isLonValid: value === '' || Math.abs(parseFloat(value)) <= 180,
    }))
  }

  const handleSetLocation = useCallback(() => {
    setLocation({
      latitude: parseFloat(lat),
      longitude: parseFloat(lon),
      timestamp: new Date().getTime(),
    })
  }, [setLocation, lat, lon])

  const handleReset = () => {
    setState((prevState) => ({
      ...prevState,
      lat: '',
      lon: '',
      isLatValid: true,
      isLonValid: true,
    }))

    setLocation(null)
  }

  const handleToggle = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      isOpen: !prevState.isOpen,
    }))
  }, [])

  const handleGetMyLocation = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      isPending: true,
    }))
    navigator.geolocation.getCurrentPosition(
      ({ coords: { latitude, longitude } }) => {
        setState((prevState) => ({
          ...prevState,
          isPending: false,
          lat: latitude,
          lon: longitude,
          isLatValid: true,
          isLonValid: true,
        }))
        setLocation({
          latitude,
          longitude,
          timestamp: new Date().getTime(),
        })
      },
      (error) => {
        console.error(error)
        setState((prevState) => ({
          ...prevState,
          isPending: false,
        }))
      },
      navigatorOptions
    )
  }, [setLocation])

  const handleTabChange = useCallback((newTab) => {
    setState((prevState) => ({ ...prevState, tab: newTab }))
  }, [])

  const handleLatLongKeyDown = useCallback(
    ({ key }) => {
      if (key === 'Enter' && isLatValid && isLonValid) {
        handleSetLocation()
      }
    },
    [handleSetLocation, isLatValid, isLonValid]
  )

  const handleKeyDown = useCallback(
    ({ key }) => {
      // escape clears everything
      if (key === 'Escape') {
        setLocation(null)
        setState(() => ({
          tab: 'find',
          lat: '',
          lon: '',
          isLatValid: true,
          isLonValid: true,
          isPending: false,
          isOpen: false,
        }))
      }
    },
    [setLocation]
  )

  const button = (
    <Box
      sx={{
        ...controlCSS,
        top: '106px',
        right: '10px',
        mt: '1px',
        cursor: 'pointer',
        width: '29px',
        '&:hover': {
          bg: '#F2F2F2',
        },
      }}
      onClick={handleToggle}
      title="Find place on map"
    >
      <SearchLocation size="1em" />
    </Box>
  )

  if (!isOpen) {
    return button
  }

  const isDisabled = !isLatValid || !isLonValid || lat === '' || lon === ''

  return (
    <>
      {button}

      <Box
        onKeyDown={handleKeyDown}
        sx={{
          ...controlCSS,
          zIndex: 20000,
          top: '65px',
          left: '10px',
          border: '1px solid #AAA',
          boxShadow: '1px 1px 8px #333',
          overflow: 'hidden',
        }}
      >
        <Flex sx={{ alignItems: 'center', gap: '1rem', mb: '1rem' }}>
          <Text
            sx={{
              ml: '0.5em',
              mr: '1rem',
              flex: '1 1 auto',
              fontWeight: 'bold',
              fontSize: 2,
            }}
          >
            Find a location on the map
          </Text>

          <Button
            variant="close"
            onClick={handleToggle}
            tabIndex="-1"
            sx={{ flex: '0 0 auto', margin: 0, p: 0, fontSize: '0.8rem' }}
          >
            <TimesCircle size="1.5em" />
          </Button>
        </Flex>

        <Box sx={{ mx: '-7px' }}>
          <Tabs
            tabs={tabs}
            activeTab={tab}
            activeVariant="tabs.active"
            variant="tabs.default"
            onChange={handleTabChange}
          />
        </Box>

        {tab === 'find' ? (
          <Box
            sx={{
              width: '334px',
              mx: '-7px',
              mb: '-6px',
              //   minHeight: '100px',
              pt: '0.25rem',
            }}
          >
            <Search />
          </Box>
        ) : (
          <Box sx={{ width: '320px' }}>
            {isPending ? (
              <Flex
                sx={{
                  justifyContent: 'center',
                  alignItems: 'center',
                  height: '80px',
                }}
              >
                <Spinner size="2em" />
              </Flex>
            ) : (
              <>
                <Grid columns={2} gap={0} sx={{ mt: '0.5rem' }}>
                  <Flex sx={{ justifyContent: 'center' }}>
                    <Text>latitude</Text>
                  </Flex>

                  <Flex sx={{ justifyContent: 'center' }}>
                    <Text>longitude</Text>
                  </Flex>

                  <Flex sx={{ justifyContent: 'center' }}>
                    <Input
                      type="number"
                      onChange={handleLatitudeChange}
                      onKeyDown={handleLatLongKeyDown}
                      value={lat}
                      variant={isLatValid ? null : 'input-invalid'}
                      sx={{
                        ...(!isLatValid ? invalidInputCSS : inputCSS),
                      }}
                    />
                  </Flex>
                  <Flex sx={{ justifyContent: 'center' }}>
                    <Input
                      type="number"
                      onChange={handleLongitudeChange}
                      onKeyDown={handleLatLongKeyDown}
                      value={lon}
                      variant={isLonValid ? null : 'input-invalid'}
                      sx={{
                        ...(!isLonValid ? invalidInputCSS : inputCSS),
                      }}
                    />
                  </Flex>
                </Grid>

                <Flex
                  sx={{
                    justifyContent: 'flex-end',
                    alignItems: 'center',
                    mt: '1rem',
                    mr: '0.5rem',
                    fontSize: 0,
                    gap: '0.5rem',
                    button: {
                      px: '0.5em',
                      py: '0.25em',
                      fontSize: 1,
                    },
                  }}
                >
                  {hasGeolocation ? (
                    <Button
                      onClick={handleGetMyLocation}
                      sx={{
                        border: 'none',
                        color: 'link',
                        backgroundColor: 'transparent !important',
                        mr: '1rem',
                      }}
                    >
                      <Flex sx={{ alignItems: 'center', gap: '0.25rem' }}>
                        <LocationArrow size="1em" />
                        <Text>use my location</Text>
                      </Flex>
                    </Button>
                  ) : null}

                  <Button
                    variant="secondary"
                    onClick={handleReset}
                    sx={{ '&:hover': { bg: 'grey.2' } }}
                  >
                    <Flex sx={{ alignItems: 'center', gap: '0.25rem' }}>
                      <Box sx={{ color: 'grey.8' }}>
                        <TrashAlt size="1em" />
                      </Box>
                      <Text>reset</Text>
                    </Flex>
                  </Button>

                  <Button
                    sx={{ cursor: isDisabled ? 'not-allowed' : 'pointer' }}
                    disabled={isDisabled}
                    variant={isDisabled ? 'secondary' : 'primary'}
                    onClick={handleSetLocation}
                  >
                    <Flex
                      sx={{
                        alignItems: 'center',
                        gap: '0.25rem',
                        color: isDisabled ? 'grey.6' : '#FFF',
                      }}
                    >
                      <Box sx={{ mt: '-2px' }}>
                        <SearchLocation size="1em" />
                      </Box>
                      <Text>GO</Text>
                    </Flex>
                  </Button>
                </Flex>
              </>
            )}
          </Box>
        )}
      </Box>
    </>
  )
}

// TODO: memo?
export default FindLocation
