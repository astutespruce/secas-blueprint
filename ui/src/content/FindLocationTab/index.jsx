import React, { memo, useCallback, useState } from 'react'
import { Box, Button, Flex, Heading, Text, Spinner } from 'theme-ui'
import { LocationArrow } from '@emotion-icons/fa-solid'

import { Search, useSearch } from 'components/search'
import { hasGeolocation } from 'util/dom'

const navigatorOptions = {
  enableHighAccuracy: false,
  maximumAge: 0,
  timeout: 6000,
}

// Tab is only displayed in mobile mode; a different map widget is used for
// desktop mode
const FindLocationTab = () => {
  const [{ error, isPending }, setState] = useState({
    error: null,
    isPending: false,
  })
  const { setLocation, query } = useSearch()

  const handleGetMyLocation = useCallback(() => {
    setState(() => ({ isPending: true, error: false }))

    navigator.geolocation.getCurrentPosition(
      ({ coords: { latitude, longitude } }) => {
        setState(() => ({ isPending: false }))
        setLocation({
          latitude,
          longitude,
          timestamp: new Date().getTime(),
        })
      },
      (err) => {
        setState(() => ({ isPending: false, error: true }))
        console.error(err)
      },
      navigatorOptions
    )
  }, [setLocation])

  return (
    <Box as="section" sx={{ py: '1.5rem' }}>
      <Heading as="h3" sx={{ mb: '0.5rem', pl: '1rem', pr: '2rem' }}>
        Find a location on the map
      </Heading>
      <Box
        sx={{
          '.search-field-container': {
            px: '1rem',
            py: '0.5rem',
            bg: 'grey.1',
          },
          '.search-field': {
            bg: '#FFF',
          },
        }}
      >
        <Search />
      </Box>

      {hasGeolocation && query === '' ? (
        <Flex sx={{ mt: '2rem', justifyContent: 'center' }}>
          {isPending ? (
            <Flex
              sx={{
                color: 'grey.8',
                justifyContent: 'center',
                px: '1rem',
                gap: '1rem',
              }}
            >
              <Spinner />
              <Text>Fetching your location from your device</Text>
            </Flex>
          ) : (
            <Flex sx={{ alignItems: 'center', flexDirection: 'column' }}>
              <Button onClick={handleGetMyLocation} sx={{ fontSize: 1 }}>
                <Flex sx={{ alignItems: 'center', gap: '1rem' }}>
                  <Box sx={{ flex: '0 0 auto' }}>
                    <LocationArrow size="1.25em" />
                  </Box>
                  <Text sx={{ flex: '1 1 auto' }}>Go to my location</Text>
                </Flex>
              </Button>
              {error ? (
                <Text sx={{ color: 'grey.8', mt: '2rem', px: '1rem' }}>
                  We&apos;re sorry, there was an error trying to get your
                  current location. Your browser may not have sufficient
                  permissions on your device to determine your location. You can
                  also try again.
                </Text>
              ) : null}
            </Flex>
          )}
        </Flex>
      ) : null}
    </Box>
  )
}

export default memo(FindLocationTab)
