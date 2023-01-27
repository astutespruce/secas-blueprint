import React, { useMemo } from 'react'
import { Box, Button, Flex, Heading, Text } from 'theme-ui'
import { SlidersH, TimesCircle } from '@emotion-icons/fa-solid'

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

  const { filters, setFilters, resetFilters } = useMapData()
  const numFilters = Object.values(filters).filter(
    ({ enabled }) => enabled
  ).length

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

  console.log('blueprint', blueprint)

  return (
    // TODO: header help text?
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
        {/* <Flex
          sx={{
            flex: '0 0 auto',
            justifyContent: 'space-between',
            pt: '1rem',
            pb: '0.5rem',
            px: '0.5rem',
            borderBottom: '1px solid',
            borderBottomColor: 'grey.1',
          }}
        >
          <Flex sx={{ alignItems: 'center' }}>
            <Box sx={{ mr: '0.5rem' }}>
              <SlidersH size="1.5rem" />
            </Box>
            <Heading as="h3">Pixel filters</Heading>
          </Flex>
          <Flex
            sx={{
              justifyContent: 'flex-end',
              alignItems: 'center',

              visibility: numFilters > 0 ? 'visible' : 'hidden',
            }}
          >
            <Button
              onClick={resetFilters}
              sx={{ fontSize: 0, py: '0.2em', bg: 'accent', px: '0.5rem' }}
            >
              <Flex sx={{ alignItems: 'center' }}>
                <Box sx={{ mr: '0.25em' }}>
                  <TimesCircle size="1em" />
                </Box>
                <Text>reset {numFilters} filter{numFilters > 1 ? 's' : ''}</Text>
              </Flex>
            </Button>
          </Flex>
        </Flex> */}

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
