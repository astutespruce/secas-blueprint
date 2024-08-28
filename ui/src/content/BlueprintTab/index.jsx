import React, { useMemo } from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Text } from 'theme-ui'

import {
  blueprint as allPriorities,
  corridors as corridorCategories,
  subregions as subregionInfo,
} from 'config'
import { OutboundLink } from 'components/link'
import NeedHelp from 'content/NeedHelp'
import { ifNull, setIntersection, sortByFunc } from 'util/data'

import BlueprintChart from './BlueprintChart'
import CorridorsChart from './CorridorsChart'
import CorridorCategories from './CorridorCategories'
import PriorityCategories from './PriorityCategories'

const BlueprintTab = ({
  type,
  blueprint,
  corridors,
  subregions,
  outsideSEPercent,
}) => {
  const marineSubregions = useMemo(
    () =>
      new Set(
        subregionInfo
          .filter(({ marine }) => marine)
          .map(({ subregion }) => subregion)
      ),
    []
  )

  // Note: incoming priorities are in descending order but percents
  // are stored in ascending order
  const priorityCategories = allPriorities
    .slice()
    .reverse()
    .map(({ color, ...rest }) => ({
      ...rest,
      // add transparency to match map
      color: `${color}bf`,
    }))

  const corridorsPresent = {}
  if (corridors !== null) {
    if (type === 'pixel') {
      corridorCategories.forEach(({ value, type: corridorType }) => {
        if (corridorType) {
          corridorsPresent[corridorType] =
            corridorsPresent[corridorType] || corridors === value
        }
      })
    } else if (corridors.length > 0) {
      corridorCategories.forEach(({ value, type: corridorType }) => {
        if (corridorType) {
          corridorsPresent[corridorType] =
            corridorsPresent[corridorType] || corridors[value] > 0
        }
      })
    }
  }

  // filter legend for corridors based on which ones are present
  const filterCorridors = ({ type: corridorType }) => {
    switch (corridorType) {
      case 'caribbean': {
        return corridorsPresent.caribbean || subregions.has('Caribbean')
      }
      case 'marine': {
        return (
          corridorsPresent.marine ||
          setIntersection(subregions, marineSubregions).size > 0
        )
      }
      case 'inland': {
        return (
          corridorsPresent.inland ||
          (type === 'subwatershed' && !subregions.has('Caribbean')) ||
          (type === 'pixel' &&
            setIntersection(subregions, marineSubregions).size === 0 &&
            !subregions.has('Caribbean'))
        )
      }
      default: {
        return type === 'pixel'
      }
    }
  }

  return (
    <Box sx={{ py: '2rem', pl: '1rem', pr: '2rem' }}>
      <Box as="section">
        <Heading as="h3">Southeast Blueprint 2024 Priority</Heading>
        <Text sx={{ color: 'grey.9' }}>
          for a connected network of lands and waters
        </Text>
        {type !== 'pixel' ? (
          <BlueprintChart
            categories={priorityCategories}
            blueprint={blueprint}
            outsideSEPercent={outsideSEPercent}
          />
        ) : null}
        {outsideSEPercent < 100 ? (
          <PriorityCategories
            categories={priorityCategories.slice().reverse()}
            value={type === 'pixel' ? blueprint : null}
          />
        ) : null}
      </Box>

      <Box as="section">
        <Text
          sx={{
            mt: '2rem',
            bg: 'grey.1',
            ml: '-1rem',
            mr: '-2rem',
            py: '1rem',
            pl: '1rem',
            pr: '2rem',
          }}
        >
          <Heading as="h3">Hubs and Corridors</Heading>
        </Text>

        {type !== 'pixel' ? (
          <CorridorsChart
            categories={corridorCategories.map(({ value, color, ...rest }) => ({
              ...rest,
              value,
              color: value === 0 ? '#ffebc2' : color,
            }))}
            // sort corridor values to match categories
            corridors={corridorCategories
              .map(({ value, sort }) => ({ value: corridors[value], sort }))
              .sort(sortByFunc('sort'))
              .map(({ value }) => value)}
            outsideSEPercent={outsideSEPercent}
          />
        ) : null}

        {outsideSEPercent < 100 ? (
          <CorridorCategories
            categories={corridorCategories.filter(filterCorridors)}
            value={type === 'pixel' ? ifNull(corridors, 0) : null}
          />
        ) : null}
      </Box>

      {type === 'subwatershed' || type === 'marine hex' ? (
        <Box
          sx={{
            color: 'grey.9',
            fontSize: 0,
            mt: '2rem',
            pt: '2rem',
            borderTop: '1px solid',
            borderTopColor: 'grey.2',
          }}
        >
          {type === 'subwatershed' ? (
            <>
              Subwatershed boundary is based on the{' '}
              <OutboundLink to="https://www.usgs.gov/national-hydrography/watershed-boundary-dataset">
                National Watershed Boundary Dataset
              </OutboundLink>{' '}
              (2023), U.S. Geological Survey.
            </>
          ) : (
            <>
              Hexagon boundary is based on 40 km<sup>2</sup> hexagons developed
              by the{' '}
              <OutboundLink to="https://www.sciencebase.gov/catalog/item/5ba9378fe4b08583a5ca0937">
                U.S. Environmental Protection Agency
              </OutboundLink>{' '}
              and extended into the Gulf of Mexico by the{' '}
              <OutboundLink to="https://www.boem.gov/gommapps">
                Gulf of Mexico Marine Assessment Program for Protected Species
              </OutboundLink>{' '}
              (GoMMAPPS). Gulf of Mexico hexagons provided by the NOAA Southeast
              Fisheries Science Center. Similar hexagons were generated in the
              U.S. Caribbean for internal use by the Southeast Conservation
              Adaptation Strategy (2023).
            </>
          )}
        </Box>
      ) : null}

      <NeedHelp />
    </Box>
  )
}

BlueprintTab.propTypes = {
  type: PropTypes.string.isRequired,
  blueprint: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]),
  corridors: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.number),
    PropTypes.number,
  ]),
  subregions: PropTypes.object,
  outsideSEPercent: PropTypes.number,
}

BlueprintTab.defaultProps = {
  blueprint: [],
  corridors: [],
  subregions: new Set(),
  outsideSEPercent: 0,
}

export default BlueprintTab
