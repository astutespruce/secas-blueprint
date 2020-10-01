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
  { id: 'unit-map', label: 'Map' },
  { id: 'unit-priorities', label: 'Priorities' },
  // { id: 'unit-indicators', label: 'Indicators' },
  { id: 'unit-threats', label: 'Threats' },
  { id: 'unit-partners', label: 'Partners' },
]

const Tabs = ({ tab, hasSelectedUnit, onChange }) => {
  return (
    <BaseTabs
      tabs={hasSelectedUnit ? unitTabs : tabs}
      activeTab={tab}
      activeVariant="tabs.mobileActive"
      variant="tabs.mobile"
      onChange={onChange}
    />
  )
}

Tabs.propTypes = {
  tab: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  hasSelectedUnit: PropTypes.bool,
}

Tabs.defaultProps = {
  hasSelectedUnit: false,
}

export default Tabs
