import React, { useState, useCallback, useEffect } from 'react'
import PropTypes from 'prop-types'

import { Box, Flex, Grid, Text } from 'theme-ui'

import Icon from './Icon'

const Tabs = ({ tabs, activeTab, variant, activeVariant, onChange }) => {
  const [tab, setTab] = useState(activeTab || tabs[0].id)

  useEffect(() => {
    if (activeTab !== tab) {
      setTab(activeTab)
    }
  }, [activeTab, tab])

  const handleClick = useCallback(
    (id) => () => {
      setTab(() => id)
      onChange(id)
    },
    [onChange]
  )

  return (
    <Grid
      as="nav"
      gap={0}
      columns={tabs.length}
      sx={{
        alignItems: 'center',
        fontSize: ['10px', 0, 1],
      }}
    >
      {tabs.map(({ id, label }) => (
        <Flex
          key={id}
          onClick={handleClick(id)}
          variant={
            id === tab
              ? activeVariant || 'tabs.active'
              : variant || 'tabs.default'
          }
          sx={{
            flexDirection: ['column', 'column', 'row'],
            alignItems: 'center',
            justifyContent: 'center',
            flex: '1 0 auto',
            p: '0.5em',
            height: '100%',
          }}
        >
          <Box>
            <Icon name={id} sx={{ width: '1.5em', height: '1.5em' }} />
          </Box>
          <Text sx={{ ml: [0, '0.5em'], textAlign: ['center', 'unset'] }}>
            {label}
          </Text>
        </Flex>
      ))}
    </Grid>
  )
}

Tabs.propTypes = {
  tabs: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  onChange: PropTypes.func.isRequired,
  activeTab: PropTypes.string,
  variant: PropTypes.string,
  activeVariant: PropTypes.string,
}

Tabs.defaultProps = {
  activeTab: null,
  variant: PropTypes.string,
  activeVariant: PropTypes.string,
}

export default Tabs
