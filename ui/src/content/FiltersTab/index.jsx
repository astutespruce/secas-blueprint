import React, { useMemo } from 'react'
import { Flex } from 'theme-ui'

import {
  useBlueprintPriorities,
  useCorridors,
  useIndicators,
  useMapData,
  useSLR,
  useUrban,
} from 'components/data'
import { indexBy } from 'util/data'
import FilterGroup from './FilterGroup'

const FiltersTab = () => {
  const { all: blueprint } = useBlueprintPriorities()
  const corridors = useCorridors()

  const {
    ecosystems: rawEcosystems,
    indicators: {
      // base is only input with indicators
      base: { indicators: rawIndicators },
    },
  } = useIndicators()

  const { depth, nodata: slrNodata } = useSLR()
  const urban = useUrban()

  const { filters, setFilters } = useMapData()

  // nest indicators under ecosystems
  const { priorities, threats, ecosystems } = useMemo(
    () => {
      const indicators = indexBy(rawIndicators, 'id')

      return {
        priorities: [
          {
            id: 'blueprint',
            label: 'Blueprint priority',
            values: blueprint.slice().reverse().slice(1, blueprint.length),
          },
          {
            id: 'corridors',
            label: 'Hubs and corridors',
            values: corridors,
            description:
              'The Blueprint uses a least-cost path connectivity analysis to identify corridors that link hubs across the shortest distance possible, while also routing through as much Blueprint priority as possible.',
          },
        ],
        threats: [
          {
            id: 'urban',
            label: 'Probability of urbanization by 2060',
            values: urban
              .slice()
              // values are not in order and need to be sorted in ascending order
              .sort(({ value: a }, { value: b }) => (a > b ? 1 : -1)),
            description:
              'Past and current (2019) urban levels based on developed land cover classes from the National Land Cover Database. Future urban growth estimates derived from the FUTURES model. Data provided by the Center for Geospatial Analytics, NC State University.',
          },
          {
            id: 'slr',
            label: 'Flooding extent by projected sea-level rise',
            values: depth
              .map(({ label, ...rest }) => ({
                ...rest,
                label: `${label} feet`,
              }))
              .concat(slrNodata),
            description:
              'Sea level rise estimates derived from the NOAA sea-level rise inundation data',
          },
        ],
        ecosystems: rawEcosystems.map(
          ({ indicators: ecosystemIndicators, ...ecosystem }) => ({
            ...ecosystem,
            indicators: ecosystemIndicators.map((id) => indicators[id]),
          })
        ),
      }
    },

    // intentionally omitting dependencies; nothing changes after mount
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  return (
    <>
      <Flex
        sx={{
          flexDirection: 'column',
          overflowY: 'auto',
          flex: '1 1 auto',
          height: '100%',
          position: 'relative', // prevents layout scroll issue on page
        }}
      >
        <FilterGroup
          id="priorities"
          label="Priorities"
          color="#FFF"
          borderColor="#FFF"
          entries={priorities}
          filters={filters}
          onChange={setFilters}
        />
        <FilterGroup
          id="threats"
          label="Threats"
          color="#ffffe9"
          borderColor="#fffcc2"
          entries={threats}
          filters={filters}
          onChange={setFilters}
        />
        {ecosystems.map((ecosystem) => (
          <FilterGroup
            key={ecosystem.id}
            {...ecosystem}
            entries={ecosystem.indicators}
            filters={filters}
            onChange={setFilters}
          />
        ))}
      </Flex>
    </>
  )
}

export default FiltersTab
