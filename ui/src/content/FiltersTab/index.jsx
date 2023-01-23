import React, { useState, useMemo } from 'react'
import { Flex } from 'theme-ui'

import { useIndicators, useMapData } from 'components/data'
import { indexBy } from 'util/data'
import Ecosystem from './Ecosystem'

const FiltersTab = () => {
  const {
    ecosystems: rawEcosystems,
    indicators: {
      // base is only input with indicators
      base: { indicators: rawIndicators },
    },
  } = useIndicators()

  const { filters, setFilters } = useMapData()

  // nest indicators under ecosystems
  const ecosystems = useMemo(
    () => {
      const indicators = indexBy(rawIndicators, 'id')
      return rawEcosystems.map(
        ({ indicators: ecosystemIndicators, ...ecosystem }) => ({
          ...ecosystem,
          indicators: ecosystemIndicators.map((id) => indicators[id]),
        })
      )
    },

    // intentionally omitting dependencies; nothing changes after mount
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  // console.log('ecosystems', ecosystems, filters)
  console.log('rerender filters tab', filters)

  return (
    // TODO: header help text?
    <Flex
      sx={{
        flexDirection: 'column',
        overflowY: 'auto',
        flex: '1 1 auto',
        height: '100%',
        position: 'relative', // prevents layout scroll issue on page
      }}
    >
      {ecosystems.map((ecosystem) => (
        <Ecosystem
          key={ecosystem.id}
          {...ecosystem}
          filters={filters}
          onChange={setFilters}
        />
      ))}
    </Flex>
  )
}

export default FiltersTab
