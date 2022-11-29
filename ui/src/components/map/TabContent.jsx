import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import {
  InfoTab,
  ContactTab,
  FindLocationTab,
  BlueprintTab,
  IndicatorsTab,
  ThreatsTab,
  PartnersTab,
} from 'content'

const TabContent = ({ tab, mapData }) => {
  if (mapData === null) {
    switch (tab) {
      case 'info': {
        return <InfoTab />
      }
      case 'find': {
        return <FindLocationTab />
      }
      case 'contact': {
        return <ContactTab />
      }
      default: {
        // includes 'map
        return null
      }
    }
  }

  const {
    type,
    isLoading,
    inputId,
    blueprint,
    corridors,
    outsideSEPercent,
    rasterizedAcres,
    indicators,
    ecosystems,
    slr,
    urban,
    ownership,
    protection,
    protectedAreas,
    ltaSearch,
  } = mapData

  if (isLoading) {
    return <Box sx={{ textAlign: 'center', mt: '1rem' }}>Loading...</Box>
  }

  if (inputId === null) {
    return (
      <Flex sx={{ py: '2rem', pl: '1rem', pr: '2rem', alignItems: 'center' }}>
        <Box sx={{ flex: '0 0 auto', mr: '1rem', color: 'orange' }}>
          <ExclamationTriangle size="2em" />
        </Box>
        <Text sx={{ color: 'grey.8', flex: '1 1 auto' }}>
          Area is outside Southeast Base Blueprint data extent.
          <br />
          No pixel-level details are available for this area.
        </Text>
      </Flex>
    )
  }

  switch (tab) {
    case 'selected-priorities': {
      return (
        <BlueprintTab
          type={type}
          blueprint={blueprint}
          corridors={corridors}
          inputId={inputId}
          outsideSEPercent={outsideSEPercent}
          ecosystems={ecosystems}
          {...mapData}
        />
      )
    }
    case 'selected-indicators': {
      return (
        <IndicatorsTab
          type={type}
          inputId={inputId}
          indicators={indicators}
          outsideSEPercent={outsideSEPercent}
          rasterizedAcres={rasterizedAcres}
        />
      )
    }
    case 'selected-threats': {
      return <ThreatsTab unitType={type} slr={slr} urban={urban} />
    }
    case 'selected-partners': {
      return (
        <PartnersTab
          type={type}
          ownership={ownership}
          protection={protection}
          protectedAreas={protectedAreas}
          ltaSearch={ltaSearch}
        />
      )
    }
    default: {
      // includes 'mobile-selected-map'
      return null
    }
  }
}

TabContent.propTypes = {
  tab: PropTypes.string.isRequired,
  mapData: PropTypes.object,
}

TabContent.defaultProps = {
  mapData: null,
}

export default TabContent
