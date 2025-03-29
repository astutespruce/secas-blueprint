import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import {
  InfoTab,
  FiltersTab,
  FindLocationTab,
  ContactTab,
  BlueprintTab,
  IndicatorsTab,
  MoreInfoTab,
} from 'content'

const TabContent = ({ tab, mapData }) => {
  if (mapData === null) {
    switch (tab) {
      case 'info': {
        return <InfoTab />
      }
      case 'filter': {
        return <FiltersTab />
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
    blueprint = null,
    corridors,
    subregions,
    outsideSEPercent,
    rasterizedAcres,
    indicators,
    slr,
    urban,
    wildfireRisk,
    protectedAreas,
    protectedAreasList,
    numProtectedAreas,
  } = mapData

  if (isLoading) {
    return <Box sx={{ textAlign: 'center', mt: '1rem' }}>Loading...</Box>
  }

  if (blueprint === null) {
    return (
      <>
        <Flex sx={{ py: '2rem', pl: '1rem', pr: '2rem', alignItems: 'center' }}>
          <Box sx={{ flex: '0 0 auto', mr: '1rem', color: 'orange' }}>
            <ExclamationTriangle size="2em" />
          </Box>
          <Text sx={{ color: 'grey.8', flex: '1 1 auto' }}>
            <b>No pixel-level details are available for this area.</b>
          </Text>
        </Flex>
      </>
    )
  }

  switch (tab) {
    case 'selected-priorities': {
      return (
        <BlueprintTab
          type={type}
          blueprint={blueprint}
          corridors={corridors}
          subregions={subregions}
          outsideSEPercent={outsideSEPercent}
          {...mapData}
        />
      )
    }
    case 'selected-indicators': {
      return (
        <IndicatorsTab
          type={type}
          indicators={indicators}
          outsideSEPercent={outsideSEPercent}
          rasterizedAcres={rasterizedAcres}
        />
      )
    }
    case 'selected-more-info': {
      return (
        <MoreInfoTab
          type={type}
          slr={slr}
          urban={urban}
          wildfireRisk={wildfireRisk}
          subregions={subregions}
          protectedAreas={protectedAreas}
          protectedAreasList={protectedAreasList}
          numProtectedAreas={numProtectedAreas}
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
