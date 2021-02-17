import React from 'react'
import PropTypes from 'prop-types'

import { Tabs as BaseTabs } from 'components/tabs'

const tabs = [
  { id: 'info', label: 'Info' },
  { id: 'map', label: 'Map' },
  { id: 'find', label: 'Find Location' },
  { id: 'contact', label: 'Contact' },
]

const unitTabs = [
  { id: 'mobile-selected-map', label: 'Map' },
  { id: 'selected-priorities', label: 'Priorities' },
  // { id: 'selected-indicators', label: 'Indicators' },
  { id: 'selected-threats', label: 'Threats' },
  { id: 'selected-partners', label: 'Partners' },
]

const Tabs = ({ tab, hasMapData, onChange }) => (
  <BaseTabs
    tabs={hasMapData ? unitTabs : tabs}
    activeTab={tab}
    activeVariant="tabs.mobileActive"
    variant="tabs.mobile"
    onChange={onChange}
  />
)

Tabs.propTypes = {
  tab: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  hasMapData: PropTypes.bool,
}

Tabs.defaultProps = {
  hasMapData: false,
}

export default Tabs
