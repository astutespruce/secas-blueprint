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
    blueprint_total: blueprintAcres,
    shape_mask: analysisAcres,
    indicators,
    ecosystems,
    slr,
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
          ecosystems={ecosystems}
          {...mapData}
        />
      )
    }
    case 'selected-indicators': {
      return (
        <IndicatorsTab
          type={type}
          blueprintAcres={blueprintAcres}
          analysisAcres={analysisAcres}
          indicators={indicators}
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
