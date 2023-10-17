import React, { useMemo } from 'react'
import { Box, Flex } from 'theme-ui'

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
            // IMPORTANT: values are a subset that acts as a proxy for their
            // corresponding rawValues; all rawValues are toggled as each entry
            // is toggled
            values: [
              {
                value: 1,
                rawValues: [1, 2],
                label: 'Corridors',
                description:
                  'inland corridors connect inland hubs; marine and estuarine corridors connect marine hubs within broad marine mammal movement areas.',
              },
              {
                value: 3,
                rawValues: [3, 4],
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
              'Past and current (2021) urban levels based on developed land cover classes from the National Land Cover Database. Future urban growth estimates derived from the FUTURES model. Data provided by the Center for Geospatial Analytics, NC State University.',
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
        <Box
          sx={{ px: '1rem', py: '0.5rem', lineHeight: 1.2, color: 'grey.8' }}
        >
          Filters can help you find the part of the Blueprint that aligns with
          your mission, interest, or specific question. Enable the filters below
          to narrow down the Blueprint to the part that falls within a range of
          values for one or more layers.
        </Box>
        <FilterGroup
          id="blueprint"
          label="Filter by priorities"
          color="#4d004b0d"
          borderColor="#4d004b2b"
          entries={priorities}
          filters={filters}
          onChange={setFilters}
        />
        <FilterGroup
          id="threats"
          label="Filter by threats"
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
            label={`Filter by ${ecosystem.label.toLowerCase()} indicators`}
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
