import React, { useMemo, useCallback } from 'react'
import { Flex } from 'theme-ui'

import {
  useBlueprintPriorities,
  useIndicators,
  useMapData,
  useSLR,
  useUrban,
} from 'components/data'
import { indexBy, sortByFunc } from 'util/data'
import FilterGroup from './FilterGroup'

const FiltersTab = () => {
  const { all: blueprint } = useBlueprintPriorities()

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
            values: blueprint
              .slice()
              .sort(sortByFunc('value'))
              .slice(1, blueprint.length),
          },
          {
            id: 'corridors',
            label: 'Hubs and corridors',
            // IMPORTANT: values are a custom range that are unpacked to correct
            // values in handlePriorityFilters below; only endpoints of range
            // are used
            values: [
              {
                value: 1,
                label: 'Corridors',
                description:
                  'inland corridors connect inland hubs; marine and estuarine corridors connect marine hubs within broad marine mammal movement areas.',
              },
              {
                value: 2,
                label: 'Hubs',
                description:
                  'inland hubs are large patches (~5,000+ acres) of highest priority Blueprint areas and/or protected lands; marine and estuarine hubs are large estuaries and large patches (~5,000+ acres) of highest priority Blueprint areas.',
              },
            ],
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
              .sort(sortByFunc('value')),
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

  const handlePriorityFilters = useCallback(
    ({ id, enabled, range }) => {
      if (id === 'corridors' && enabled) {
        // custom handler to unpack the values used for the range for filtering
        // to the underying pixel range

        let expandedRange = null
        if (range[1] === 1) {
          // if only showing corridors, show inland & marine
          expandedRange = [1, 2]
        } else if (range[0] === 2) {
          // if only showing hubs, show inland & marine
          expandedRange = [3, 4]
        } else {
          // otherwise show full value range
          expandedRange = [1, 4]
        }

        setFilters({ id, enabled, range: expandedRange })
      } else {
        setFilters({ id, enabled, range })
      }
    },
    // intentionally omitting dependencies; nothing changes after mount
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  // re-pack corridor full range to [1,2] range used by slider
  const { blueprint: blueprintFilter, corridors: corridorsFilter } = filters
  const priorityFilterState = {
    blueprint: blueprintFilter,
    corridors: {
      enabled: corridorsFilter.enabled,
      range: [
        corridorsFilter.range[0] === 3 ? 2 : 1,
        corridorsFilter.range[1] === 2 ? 1 : 2,
      ],
    },
  }

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
          id="blueprint"
          label="Priorities"
          color="#4d004b0d"
          borderColor="#4d004b2b"
          entries={priorities}
          filters={priorityFilterState}
          onChange={handlePriorityFilters}
        />
        <FilterGroup
          id="threats"
          label="Threats"
          color="#f3c6a830"
          borderColor="#f3c6a891"
          entries={threats}
          filters={filters}
          onChange={setFilters}
        />
        {ecosystems.map((ecosystem) => (
          <FilterGroup
            key={ecosystem.id}
            {...ecosystem}
            label={`${ecosystem.label} indicators`}
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
