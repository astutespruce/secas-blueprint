import React, { useMemo } from 'react'
import { Box, Flex, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import {
  blueprint,
  corridors,
  ecosystems as rawEcosystems,
  indicators as rawIndicators,
  subregions as rawSubregions,
  urban,
  slrDepth,
  slrNodata,
  wildfireRisk,
  protectedAreas,
} from 'config'
import { useMapData } from 'components/data'
import { indexBy, sortByFunc, setIntersection } from 'util/data'
import FilterGroup from './FilterGroup'

const FiltersTab = () => {
  const subregionsIndex = indexBy(rawSubregions, 'subregion')

  const { filters, setFilters, visibleSubregions } = useMapData()

  // nest indicators under ecosystems
  const { priorities, otherInfo, ecosystems } = useMemo(
    () => {
      const indicators = indexBy(rawIndicators, 'id')

      return {
        priorities: [
          {
            id: 'blueprint',
            label: 'Blueprint priority',
            description:
              'The Blueprint identifies priority areas based on a suite of natural and cultural resource indicators representing terrestrial, freshwater, and marine ecosystems.',
            values: blueprint
              .slice()
              .sort(sortByFunc('value'))
              .slice(1, blueprint.length)
              .reverse(),
          },
          {
            id: 'corridors',
            label: 'Hubs and corridors',
            values: corridors.filter(({ value }) => value > 0),
            description:
              'The Blueprint uses a least-cost path connectivity analysis to identify corridors that link hubs across the shortest distance possible, while also routing through as much Blueprint priority as possible.',
          },
        ],
        ecosystems: rawEcosystems.map(
          ({ indicators: ecosystemIndicators, ...ecosystem }) => ({
            ...ecosystem,
            indicators: ecosystemIndicators.map((id) => ({
              ...indicators[id],
              // sort indicator values in descending order
              values: indicators[id].values.slice().reverse(),
            })),
          })
        ),
        otherInfo: [
          {
            id: 'urban',
            label: 'Probability of urbanization by 2060',
            values: urban
              .slice()
              // values are not in order and need to be sorted in ascending order
              .sort(sortByFunc('value')),
            description:
              'Past and current (2021) urban levels based on developed land cover classes from the National Land Cover Database. Future urban growth estimates derived from the FUTURES model developed by the Center for Geospatial Analytics, NC State University.  Data extent limited to the inland continental Southeast.',
          },
          {
            id: 'slr',
            label: 'Flooding extent by projected sea-level rise',
            values: slrDepth
              .map(({ label, ...rest }) => ({
                ...rest,
                label: `${label} feet`,
              }))
              .concat(slrNodata),
            description:
              'Sea level rise estimates derived from the NOAA sea-level rise inundation data.',
          },
          {
            id: 'wildfireRisk',
            label: 'Wildfire likelihood (annual burn probability)',
            values: wildfireRisk,
            description:
              'Wildfire likelihood data derived from the Wildfire Risk to Communities project by the USDA Forest Service.',
          },
          {
            id: 'protectedAreas',
            label: 'Protected areas',
            values: protectedAreas,
            description:
              'Protected areas information is derived from the Protected Areas Database of the United States (PAD-US v4.0 and v3.0).',
          },
        ],
      }
    },

    // intentionally omitting dependencies; nothing changes after mount
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  if (
    visibleSubregions.size === 0 &&
    Object.values(filters).filter(({ enabled }) => enabled).length === 0
  ) {
    return (
      <Flex sx={{ py: '2rem', pl: '1rem', pr: '2rem', alignItems: 'center' }}>
        <Box sx={{ flex: '0 0 auto', mr: '1rem', color: 'orange' }}>
          <ExclamationTriangle size="2em" />
        </Box>
        <Text sx={{ color: 'grey.8', flex: '1 1 auto' }}>
          <b>No filters are available for this area.</b>
        </Text>
      </Flex>
    )
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
          entries={priorities.map((entry) => ({
            ...entry,
            canBeVisible: visibleSubregions.size > 0,
          }))}
          filters={filters}
          onChange={setFilters}
        />

        {ecosystems.map((ecosystem) => (
          <FilterGroup
            key={ecosystem.id}
            {...ecosystem}
            label={`Filter by ${ecosystem.label.toLowerCase()} indicators`}
            entries={ecosystem.indicators.map(
              ({ subregions: indicatorSubregions, ...rest }) => ({
                ...rest,
                canBeVisible:
                  setIntersection(indicatorSubregions, visibleSubregions).size >
                  0,
              })
            )}
            filters={filters}
            onChange={setFilters}
          />
        ))}

        <FilterGroup
          id="otherInfo"
          label="More filters"
          color="#f3c6a830"
          borderColor="#f3c6a891"
          entries={otherInfo.map((entry) => ({
            ...entry,
            canBeVisible:
              [...visibleSubregions].filter(
                (name) => !subregionsIndex[name].marine
              ).length > 0,
          }))}
          filters={filters}
          onChange={setFilters}
        />
      </Flex>
    </>
  )
}

export default FiltersTab
