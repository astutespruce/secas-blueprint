import React, { useCallback, useMemo } from 'react'
import { Eye, EyeSlash, LayerGroup } from '@emotion-icons/fa-solid'
import { Box, Flex, Heading, Text } from 'theme-ui'

import {
  useMapData,
  useCorridors,
  useIndicators,
  useSLR,
  useUrban,
} from 'components/data'
import { BoundModal } from 'components/modal'
import { indexBy, sortByFunc } from 'util/data'

const LayerToggle = () => {
  const { renderLayer, setRenderLayer } = useMapData()
  const corridors = useCorridors()
  const { ecosystems, indicators } = useIndicators()
  const urbanCategories = useUrban()
  const { depth: depthCategories, nodata: slrNodataCategories } = useSLR()

  const { renderLayerGroups, renderLayersIndex } = useMemo(
    () => {
      const coreLayers = [
        {
          id: 'blueprint',
          label: 'Blueprint priority',
        },
        {
          id: 'corridors',
          label: 'Hubs and corridors',
          colors: corridors
            .slice()
            .sort(sortByFunc('value'))
            .map(({ color }) => color),
          categories: corridors.filter(({ value }) => value > 0),
        },
      ]

      const threatLayers = [
        {
          id: 'urban',
          label: 'Probability of urbanization by 2060',
          colors: urbanCategories.map(({ color }) => color),
          categories: urbanCategories.filter(({ color }) => color !== null),
        },
        {
          id: 'slr',
          label: 'Flooding extent by projected sea-level rise',
          colors: depthCategories
            .concat(slrNodataCategories)
            .map(({ color }) => color),
          categories: depthCategories
            .concat(slrNodataCategories.filter(({ value }) => value !== 13))
            .map(({ label, ...rest }, i) => ({
              ...rest,
              label:
                /* eslint-disable-next-line no-nested-ternary */
                i === 1 ? `${label} foot` : i <= 10 ? `${label} feet` : label,
              outlineWidth: 1,
              outlineColor: 'grey.5',
            })),
        },
      ]

      const layers = coreLayers.concat(threatLayers)

      const groups = [
        {
          id: 'core',
          label: 'Priorities',
          layers: coreLayers,
        },
        {
          id: 'threats',
          label: 'Threats',
          layers: threatLayers,
        },
      ]

      const indicatorsIndex = indexBy(indicators.base.indicators, 'id')

      ecosystems.forEach(
        ({ id: groupId, label: groupLabel, indicators: groupIndicators }) => {
          const group = {
            id: groupId,
            label: `${groupLabel} indicators`,
            layers: groupIndicators.map((id) => {
              const { label, values, valueLabel } = indicatorsIndex[id]
              return {
                id,
                label,
                colors: values.map(({ color }) => color),
                categories: values
                  .filter(({ color }) => color !== null)
                  .reverse(),
                valueLabel,
              }
            }),
          }

          groups.push(group)
          layers.push(...group.layers)
        }
      )

      return {
        renderLayerGroups: groups,
        renderLayersIndex: indexBy(layers, 'id'),
      }
    },
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    []
  )

  const handleSetRenderLayer = useCallback(
    (id) => () => {
      if (id === 'blueprint') {
        setRenderLayer(null)
      } else {
        setRenderLayer(renderLayersIndex[id])
      }
    },
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [renderLayersIndex]
  )

  const isActiveLayer = useCallback(
    (id) =>
      (renderLayer === null && id === 'blueprint') ||
      (renderLayer && renderLayer.id === id),
    [renderLayer]
  )

  return (
    <BoundModal
      title="Choose map layer to show on map"
      anchorNode={
        <Flex
          sx={{
            alignItems: 'center',
            justifyContent: 'center',
            position: 'absolute',
            top: '10px',
            right: '50px',
            padding: '6px',
            color: 'grey.9',
            bg: '#FFF',
            pointerEvents: 'auto',
            cursor: 'pointer',
            borderRadius: '0.25rem',
            boxShadow: '2px 2px 6px #333',
          }}
          title="Choose map layer to show on map"
        >
          <LayerGroup size="1em" />
        </Flex>
      }
    >
      <Box sx={{ maxHeight: '400px', overflowY: 'auto' }}>
        {renderLayerGroups.map(({ id: groupId, label: groupLabel, layers }) => (
          <Box
            key={groupId}
            sx={{
              '&:not(:first-of-type)': {
                mt: '1rem',
                pt: '0.5rem',
                borderTop: '1px solid',
                borderTopColor: 'grey.1',
              },
            }}
          >
            {groupLabel ? <Heading as="h4">{groupLabel}</Heading> : null}
            {layers.map(({ id, label }) => (
              <Flex
                key={id}
                sx={{ alignItems: 'top', cursor: 'pointer' }}
                onClick={handleSetRenderLayer(id)}
              >
                <Box
                  sx={{
                    mr: '0.5rem',
                    color: isActiveLayer(id) ? 'inherit' : 'grey.8',
                  }}
                >
                  {isActiveLayer(id) ? (
                    <Eye size="1em" />
                  ) : (
                    <EyeSlash size="1em" />
                  )}
                </Box>
                <Text
                  sx={{
                    fontWeight: isActiveLayer(id) ? 'bold' : 'inherit',
                  }}
                >
                  {label}
                </Text>
              </Flex>
            ))}
          </Box>
        ))}
      </Box>
    </BoundModal>
  )
}

export default LayerToggle
