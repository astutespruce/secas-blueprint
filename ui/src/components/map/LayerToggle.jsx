import React, { useCallback } from 'react'
import { Eye, EyeSlash, LayerGroup } from '@emotion-icons/fa-solid'
import { Box, Flex, Heading, Text } from 'theme-ui'

import { useMapData } from 'components/data'
import { BoundModal } from 'components/modal'
import { logGAEvent } from 'util/log'

import { renderLayerGroups, renderLayersIndex } from './pixelLayers'

const LayerToggle = () => {
  const { renderLayer, setRenderLayer } = useMapData()

  const handleSetRenderLayer = useCallback(
    (id) => () => {
      setRenderLayer(renderLayersIndex[id])
      logGAEvent('set-render-layer', {
        layer: id,
      })
    },
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [renderLayersIndex]
  )

  const isActiveLayer = useCallback(
    (id) => renderLayer && renderLayer.id === id,
    [renderLayer]
  )

  return (
    <BoundModal
      title="Choose layer to show on map"
      anchorNode={
        <Flex
          className="map-button"
          sx={{
            alignItems: 'center',
            justifyContent: 'center',
            position: 'absolute',
            top: '160px',
            right: '10px',
            padding: '6px',
            color: 'grey.9',
            bg: '#FFF',
            pointerEvents: 'auto',
            cursor: 'pointer',
            borderRadius: '0.25rem',
            boxShadow: '0 0 0 2px rgba(0,0,0,.1)',
          }}
          title="Choose layer to show on map"
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
