import React, {
  useState,
  useCallback,
  useRef,
  useEffect,
  useLayoutEffect,
} from 'react'
import { Box, Button, Flex, Heading, Text } from 'theme-ui'
import { SlidersH, TimesCircle } from '@emotion-icons/fa-solid'

import { useBreakpoints } from 'components/layout'
import { useMapData } from 'components/data'
import { Tabs as MobileTabs } from 'components/layout/mobile'
import { SidebarHeader, Tabs as DesktopTabs } from 'components/layout/desktop'

import { useSearch } from 'components/search'

import Map from './Map'
import TabContent from './TabContent'

const sidebarCSS = {
  height: '100%',
  bg: '#FFF',
  flexGrow: 1,
  flexShrink: 0,
  flexBasis: ['100%', '320px', '468px', '600px'],
  maxWidth: ['100%', '320px', '468px', '600px'],
  flexDirection: 'column',
  overflowX: 'hidden',
  overflowY: 'hidden',
}

const mobileSidebarCSS = {
  ...sidebarCSS,
  position: 'absolute',
  zIndex: 10000,
  left: 0,
  right: 0,
  bottom: 0,
  top: 0,
}

const MapContainer = () => {
  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

  const {
    data: mapData,
    isLoading: isDataLoading,
    unsetData: unsetMapData,
    mapMode,
    filters,
    resetFilters,
  } = useMapData()

  const { location } = useSearch()
  const contentNode = useRef(null)

  // keep refs so we can compare state changes to previous state to reset tabs, etc
  // NOTE: we use a tab ref that parallels state so we can use in effects below
  // without those changing as tab is changed
  const tabRef = useRef(isMobile ? 'map' : 'info')
  const hasMapDataRef = useRef(false)
  const mapModeRef = useRef(mapMode)

  const [{ tab }, setState] = useState({
    tab: isMobile ? 'map' : 'info',
  })

  const numFilters = Object.values(filters).filter(
    ({ enabled }) => enabled
  ).length

  const handleTabChange = useCallback((newTab) => {
    tabRef.current = newTab
    setState((prevState) => ({
      ...prevState,
      tab: newTab,
    }))
    // scroll content to top
    contentNode.current.scrollTop = 0
  }, [])

  useEffect(() => {
    hasMapDataRef.current = mapData !== null

    console.log('selected map data', mapData)
  }, [mapData])

  useLayoutEffect(() => {
    let nextTab = tab

    if (mapMode !== mapModeRef.current) {
      mapModeRef.current = mapMode

      if (mapMode === 'filter') {
        nextTab = 'filter'
      } else if (!isMobile) {
        nextTab = 'info'
        // in mobile: keep the mode the same
        // in desktop:
        // if in pixel mode, map needs to load pixel data before showing
        // data in sidebar; default to info tab
      }
    } else {
      // if no change in available data, return
      if (hasMapDataRef.current === (mapData !== null)) {
        return
      }

      if (mapData === null) {
        nextTab = tab === 'mobile-selected-map' || isMobile ? 'map' : 'info'
      } else if (tab === 'map') {
        nextTab = 'mobile-selected-map'
      } else if (!tab.startsWith('selected-')) {
        nextTab = 'selected-priorities'
      }
    }

    if (nextTab !== tab) {
      handleTabChange(nextTab)

      // scroll content to top
      contentNode.current.scrollTop = 0
    }
  }, [mapMode, mapData, tab, isMobile, handleTabChange])

  useEffect(() => {
    // handle window resize from mobile to desktop, so that we show content again
    // if map tab previously selected

    // was mobile, now is desktop, need to show tabs again
    if (!isMobile && tabRef.current === 'map') {
      const nextTab = hasMapDataRef.current ? 'selected-priorities' : 'info'
      handleTabChange(nextTab)
    }
  }, [isMobile, handleTabChange])

  // if location is set in mobile view, automatically switch to map tab
  useEffect(() => {
    if (isMobile && location !== null && tabRef.current !== 'map') {
      handleTabChange('map')
    }
  }, [isMobile, location, handleTabChange])

  if (isMobile) {
    return (
      <Flex
        sx={{
          height: '100%',
          flex: '1 1 auto',
          flexDirection: 'column',
        }}
      >
        <Flex
          sx={{
            height: '100%',
            flex: '1 1 auto',
            overflowY: 'hidden',
            position: 'relative',
          }}
        >
          <Flex
            sx={{
              display:
                tab === 'map' || tab === 'mobile-selected-map'
                  ? 'none !important'
                  : 'flex',
              ...mobileSidebarCSS,
            }}
          >
            <Box
              ref={contentNode}
              sx={{
                height: '100%',
                overflowY: 'auto',
              }}
            >
              <TabContent
                tab={tab}
                mapData={mapData}
                isLoading={isDataLoading}
              />
            </Box>
          </Flex>

          <Map />
        </Flex>

        <Box
          sx={{
            flex: '0 0 auto',
            borderTop: '1px solid',
            borderTopColor: 'grey.9',
          }}
        >
          <MobileTabs
            tab={tab}
            mode={mapMode}
            hasMapData={mapData !== null && !isDataLoading}
            isLoading={isDataLoading}
            onChange={handleTabChange}
          />
        </Box>
      </Flex>
    )
  }

  return (
    <Flex
      sx={{
        height: '100%',
        flex: '1 1 auto',
        flexDirection: 'column',
      }}
    >
      <Flex
        sx={{
          height: '100%',
          flex: '1 1 auto',
          overflowY: 'hidden',
          position: 'relative',
        }}
      >
        <Flex
          sx={{
            display: tab === 'map' ? 'none !important' : 'flex',
            ...sidebarCSS,
          }}
        >
          {mapMode === 'filter' ? (
            <>
              <Flex
                sx={{
                  flex: '0 0 auto',
                  justifyContent: 'space-between',
                  pt: '1rem',
                  pb: '0.5rem',
                  px: '0.5rem',
                  borderBottom: '1px solid',
                  borderBottomColor: 'grey.3',
                }}
              >
                <Flex sx={{ alignItems: 'center' }}>
                  <Box sx={{ mr: '0.5rem' }}>
                    <SlidersH size="1.5rem" />
                  </Box>
                  <Heading as="h3">Pixel filters</Heading>
                </Flex>
                <Flex
                  sx={{
                    justifyContent: 'flex-end',
                    alignItems: 'center',

                    visibility: numFilters > 0 ? 'visible' : 'hidden',
                  }}
                >
                  <Button
                    onClick={resetFilters}
                    sx={{
                      fontSize: 0,
                      py: '0.2em',
                      bg: 'primary',
                      px: '0.5rem',
                    }}
                  >
                    <Flex sx={{ alignItems: 'center' }}>
                      <Box sx={{ mr: '0.25em' }}>
                        <TimesCircle size="1em" />
                      </Box>
                      <Text>
                        reset {numFilters} filter{numFilters > 1 ? 's' : ''}
                      </Text>
                    </Flex>
                  </Button>
                </Flex>
              </Flex>

              <Box
                ref={contentNode}
                sx={{
                  height: '100%',
                  overflowY: 'auto',
                }}
              >
                <TabContent
                  tab={tab}
                  mapData={mapData}
                  isLoading={isDataLoading}
                />
              </Box>
            </>
          ) : (
            <>
              {tab !== 'info' ? (
                <Box sx={{ flex: '0 0 auto' }}>
                  {mapData !== null && (
                    <SidebarHeader
                      {...mapData}
                      showClose={mapMode !== 'pixel'}
                      onClose={unsetMapData}
                    />
                  )}

                  <DesktopTabs
                    tab={tab}
                    mapMode={mapMode}
                    hasMapData={mapData !== null}
                    onChange={handleTabChange}
                  />
                </Box>
              ) : null}

              <Box
                ref={contentNode}
                sx={{
                  height: '100%',
                  overflowY: 'auto',
                }}
              >
                <TabContent
                  tab={tab}
                  mapData={mapData}
                  isLoading={isDataLoading}
                />
              </Box>
            </>
          )}
        </Flex>

        <Map />
      </Flex>
    </Flex>
  )
}

export default MapContainer
