import React, {
  useState,
  useCallback,
  useRef,
  useEffect,
  useLayoutEffect,
} from 'react'
import { Box, Flex, Text, useThemeUI } from 'theme-ui'
import { Download } from '@emotion-icons/fa-solid'

import { useBreakpoints, useSelectedUnit } from 'components/layout'
import {
  InfoTab,
  ContactTab,
  FindLocationTab,
  PrioritiesTab,
  IndicatorsTab,
  ThreatsTab,
  PartnersTab,
} from 'content'
import { Tabs as MobileTabs } from 'components/layout/mobile'
import {
  SelectedUnitHeader as DesktopSelectedUnitHeader,
  Tabs as DesktopTabs,
} from 'components/layout/desktop'

import { DownloadModal } from 'components/report'
import { useSearch } from 'components/search'
import { hasWindow } from 'util/dom'

import Map from './Map'

const MapContainer = () => {
  const {
    theme: { layout },
  } = useThemeUI()

  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

  const { selectedUnit, deselectUnit } = useSelectedUnit()

  const { location } = useSearch()

  const contentNode = useRef(null)

  // keep refs so we can compare state changes to previous state to reset tabs, etc
  // NOTE: we use a tab ref that parallels state so we can use in effects below
  // without those changing as tab is changed
  const tabRef = useRef(isMobile ? 'map' : 'info')
  const hasSelectedUnitRef = useRef(false)

  const [{ tab }, setState] = useState({
    tab: isMobile ? 'map' : 'info',
  })

  const handleTabChange = useCallback((newTab) => {
    tabRef.current = newTab
    setState((prevState) => ({
      ...prevState,
      tab: newTab,
    }))
    // scroll content to top
    contentNode.current.scrollTop = 0
  }, [])

  const [isReportModalOpen, setIsReportModalOpen] = useState(false)

  const handleReportModalClose = useCallback(() => {
    setIsReportModalOpen(() => false)
  }, [])

  const handleReportModalOpen = useCallback(() => {
    setIsReportModalOpen(() => true)
  }, [])

  useEffect(() => {
    hasSelectedUnitRef.current = selectedUnit !== null

    console.log('selectedUnit', selectedUnit)
  }, [selectedUnit])

  useLayoutEffect(() => {
    // If selected unit changed from null to unit, or unit to null,
    // we need to update the tabs.

    // if no change in selected unit status, return
    if (hasSelectedUnitRef.current === (selectedUnit !== null)) {
      return
    }

    let nextTab = tab
    if (selectedUnit === null) {
      nextTab = tab === 'unit-map' || isMobile ? 'map' : 'info'
    } else if (tab === 'map') {
      nextTab = 'unit-map'
    } else if (!tab.startsWith('unit-')) {
      nextTab = 'unit-priorities'
    }

    if (nextTab !== tab) {
      handleTabChange(nextTab)

      // scroll content to top
      contentNode.current.scrollTop = 0
    }
  }, [selectedUnit, tab, isMobile, handleTabChange])

  useEffect(() => {
    // handle window resize from mobile to desktop, so that we show content again
    // if map tab previously selected

    // was mobile, now is desktop, need to show tabs again
    if (!isMobile && tabRef.current === 'map') {
      const nextTab = hasSelectedUnitRef.current ? 'unit-priorities' : 'info'
      handleTabChange(nextTab)
    }
  }, [isMobile, handleTabChange])

  // if location is set in mobile view, automatically switch to map tab
  useEffect(() => {
    if (isMobile && location !== null && tabRef.current !== 'map') {
      handleTabChange('map')
    }
  }, [isMobile, location, handleTabChange])

  let content = null
  if (selectedUnit === null) {
    // eslint-disable-next-line default-case
    switch (tab) {
      case 'info': {
        content = <InfoTab />
        break
      }
      case 'map': {
        // don't show anything
        content = null
        break
      }
      case 'find': {
        content = <FindLocationTab />
        break
      }
      case 'contact': {
        content = <ContactTab />
        break
      }
    }
  } else {
    const {
      type: unitType,
      acres: unitAcres,
      blueprint,
      blueprint_total: blueprintAcres,
      shape_mask: analysisAcres,
      hubs_connectors: hubsConnectors,
      indicators,
      slr,
      urban,
      ownership,
      protection,
      counties,
    } = selectedUnit

    // eslint-disable-next-line default-case
    switch (tab) {
      case 'unit-map': {
        // don't show anything
        content = null
        break
      }
      case 'unit-priorities': {
        content = (
          <PrioritiesTab
            blueprint={blueprint}
            hubsConnectors={hubsConnectors}
            blueprintAcres={blueprintAcres}
          />
        )
        break
      }
      case 'unit-indicators': {
        content = (
          <IndicatorsTab
            unitType={unitType}
            blueprintAcres={blueprintAcres}
            analysisAcres={analysisAcres}
            indicators={indicators}
          />
        )
        break
      }
      case 'unit-threats': {
        content = <ThreatsTab unitType={unitType} slr={slr} urban={urban} />
        break
      }
      case 'unit-partners': {
        content = (
          <PartnersTab
            unitType={unitType}
            analysisAcres={unitAcres}
            ownership={ownership}
            protection={protection}
            counties={counties}
          />
        )
        break
      }
    }
  }

  const sidebarCSS = isMobile
    ? {
        position: isMobile ? 'absolute' : 'relative',
        zIndex: 10000,
        left: 0,
        right: 0,
        bottom: 0,
        top: 0,
      }
    : {}

  // Force exit here when building gatsby, otherwise
  // the wrong layout gets built
  if (!hasWindow) return null

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
            display: content === null ? 'none !important' : 'flex',

            height: '100%',
            bg: '#FFF',
            flexGrow: 1,
            flexShrink: 0,
            flexBasis: layout.sidebar.width,
            flexDirection: 'column',
            overflowX: 'hidden',
            overflowY: 'hidden',
            borderRightColor: layout.sidebar.borderRightColor,
            borderRightWidth: layout.sidebar.borderRightWidth,
            borderRightStyle: 'solid',
            ...sidebarCSS,
          }}
        >
          {!isMobile && (
            <Box sx={{ flex: '0 0 auto' }}>
              {selectedUnit !== null && (
                <>
                  <DesktopSelectedUnitHeader
                    name={selectedUnit.name}
                    acres={selectedUnit.acres}
                    onClose={deselectUnit}
                  />
                  <Flex
                    sx={{
                      px: '1rem',
                      pb: '0.5rem',
                      alignItems: 'center',
                      color: 'primary',
                      cursor: 'pointer',
                      '&:hover': {
                        textDecoration: 'underline',
                      },
                    }}
                    onClick={handleReportModalOpen}
                  >
                    <Download size="1rem" style={{ marginRight: '0.5rem' }} />
                    <Text>Create summary report</Text>
                  </Flex>
                </>
              )}
              <DesktopTabs
                tab={tab}
                hasSelectedUnit={selectedUnit !== null}
                onChange={handleTabChange}
              />
            </Box>
          )}

          <Box
            ref={contentNode}
            sx={{
              height: '100%',
              overflowY: 'auto',
            }}
          >
            {content}
          </Box>
        </Flex>

        <Map />
      </Flex>

      {/* Mobile footer tabs */}
      {isMobile && (
        <Box
          sx={{
            flex: '0 0 auto',
            borderTop: '1px solid',
            borderTopColor: 'grey.9',
          }}
        >
          <MobileTabs
            tab={tab}
            hasSelectedUnit={selectedUnit !== null}
            onChange={handleTabChange}
          />
        </Box>
      )}

      {isReportModalOpen && selectedUnit !== null ? (
        <DownloadModal
          id={selectedUnit.id}
          type={selectedUnit.type}
          onClose={handleReportModalClose}
        />
      ) : null}
    </Flex>
  )
}

export default MapContainer
