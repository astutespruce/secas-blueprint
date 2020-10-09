import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { Tabs as BaseTabs } from 'components/tabs'

const tabs = [
  { id: 'info', label: 'Info' },
  { id: 'find', label: 'Find Location' },
  { id: 'contact', label: 'Contact' },
]

const unitTabs = [
  { id: 'unit-blueprint', label: 'Priorities' },
  // { id: 'unit-indicators', label: 'Indicators' },
  { id: 'unit-threats', label: 'Threats' },
  { id: 'unit-partners', label: 'Partners' },
]

const Tabs = ({ tab, hasSelectedUnit, onChange }) => {
  return (
    <Box>
      <BaseTabs
        tabs={hasSelectedUnit ? unitTabs : tabs}
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
  onChange: PropTypes.func.isRequired,
  hasSelectedUnit: PropTypes.bool,
}

Tabs.defaultProps = {
  hasSelectedUnit: false,
}

export default Tabs
