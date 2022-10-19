import React from 'react'
import PropTypes from 'prop-types'
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
    blueprint,
    inputs,
    outsideSEPercent,
    rasterizedAcres,
    indicators,
    ecosystems,
    slrDepth,
    urban,
    ownership,
    protection,
    protectedAreas,
    counties,
  } = mapData

  switch (tab) {
    case 'selected-priorities': {
      return (
        <BlueprintTab
          type={type}
          blueprint={blueprint}
          inputs={inputs}
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
          inputs={inputs}
          indicators={indicators}
          outsideSEPercent={outsideSEPercent}
          rasterizedAcres={rasterizedAcres}
        />
      )
    }
    case 'selected-threats': {
      return <ThreatsTab unitType={type} slrDepth={slrDepth} urban={urban} />
    }
    case 'selected-partners': {
      return (
        <PartnersTab
          type={type}
          ownership={ownership}
          protection={protection}
          protectedAreas={protectedAreas}
          counties={counties}
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
