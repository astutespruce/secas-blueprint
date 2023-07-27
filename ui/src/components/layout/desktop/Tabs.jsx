import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { Tabs as BaseTabs } from 'components/tabs'

const defaultTabs = [
  { id: 'info', label: 'Info' },
  // { id: 'find', label: 'Find Location' },
]

const filterTabs = [
  { id: 'filter', label: 'Filter the Blueprint' },
  { id: 'find', label: 'Find Location' },
]

const unitTabs = [
  { id: 'selected-priorities', label: 'Priorities' },
  { id: 'selected-indicators', label: 'Indicators' },
  { id: 'selected-threats', label: 'Threats' },
  { id: 'selected-partners', label: 'Partners' },
]

const Tabs = ({ tab, mapMode, hasMapData, onChange }) => {
  let tabs = defaultTabs

  if (mapMode === 'filter') {
    tabs = filterTabs
  } else if (hasMapData) {
    tabs = unitTabs
  }

  return (
    <Box>
      <BaseTabs
        tabs={tabs}
        activeTab={tab}
        activeVariant="tabs.active"
        variant="tabs.default"
        onChange={onChange}
      />
    </Box>
  )
}

Tabs.propTypes = {
  tab: PropTypes.string.isRequired,
  mapMode: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  hasMapData: PropTypes.bool,
}

Tabs.defaultProps = {
  hasMapData: false,
}

export default Tabs
