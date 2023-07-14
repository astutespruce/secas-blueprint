import React, { memo, useCallback } from 'react'
import PropTypes from 'prop-types'
import { Box, Text, Flex, Button } from 'theme-ui'

import { useMapData } from 'components/data'
import { Tooltip } from 'components/tooltip'

const baseCSS = {
  position: 'absolute',
  textAlign: 'center',
  pt: '0.75em',
  pb: '0.5em',
  px: '1em',
  bg: '#FFF',
  color: 'grey.8',
  boxShadow: '0 2px 6px #666',
}

const mobileCSS = {
  ...baseCSS,
  fontSize: 0,
  left: 0,
  right: 0,
  bottom: 0,
  zIndex: 1000,
}

const desktopCSS = {
  ...baseCSS,

  fontSize: 1,
  left: '12px',
  top: 0,
  borderRadius: '0 0 1em 1em',
}

const instructionsCSS = {
  fontSize: 0,
  textAlign: 'left',
  ml: '0.5rem',
  lineHeight: 1,
}

const mobileInstructionsCSS = {
  ...instructionsCSS,
  fontSize: 'smaller',
  ml: '-0.5rem',
  mr: '-0.5rem',
  mt: '0.25rem',
}

const MapModeToggle = ({ belowMinZoom, isMobile }) => {
  const { mapMode, setMapMode } = useMapData()

  const handleFilterClick = useCallback(() => {
    setMapMode('filter')
  }, [setMapMode])

  const handlePixelClick = useCallback(() => {
    setMapMode('pixel')
  }, [setMapMode])

  const handleUnitClick = useCallback(() => {
    setMapMode('unit')
  }, [setMapMode])

  return (
    <Box sx={isMobile ? mobileCSS : desktopCSS}>
      <Flex
        sx={{
          alignItems: 'center',
          flexWrap: 'wrap',
          justifyContent: isMobile ? 'center' : null,
        }}
      >
        <Flex
          sx={{
            alignItems: 'center',
          }}
        >
          <Button
            variant="group"
            data-state={mapMode === 'unit' ? 'active' : null}
            onClick={handleUnitClick}
          >
            <Tooltip
              content="Click on any subwatershed or marine lease block to show summary data for that area, including charts of the Blueprint, indicators present, threats, and land ownership. You may need to zoom in futher to select an area."
              direction="bottom"
              maxWidth="240px"
              fontSize={0}
            >
              Summarize data
            </Tooltip>
          </Button>

          <Button
            variant="group"
            data-state={mapMode === 'pixel' ? 'active' : null}
            onClick={handlePixelClick}
          >
            <Tooltip
              content="Center the crosshairs in the middle of the map over a point on the map to show specific data for that location, including the Blueprint, indicators, present, threats, and land ownership.  You may need to zoom in further to show pixel-level details."
              direction="bottom"
              maxWidth="240px"
              fontSize={0}
            >
              Show data at a point
            </Tooltip>
          </Button>

          {/* Filter mode is not available for mobile */}
          {!isMobile ? (
            <Button
              variant="group"
              data-state={mapMode === 'filter' ? 'active' : null}
              onClick={handleFilterClick}
            >
              <Tooltip
                content="Pixel filters can help you find the part of the Blueprint that aligns with your mission, interests, or specific question. Use the filters to show areas on the map that fall within a range of values for one or more layers, including the Blueprint, hubs and corridors, underlying indicators, and threats."
                direction="bottom"
                maxWidth="240px"
                fontSize={0}
              >
                Filter the Blueprint
              </Tooltip>
            </Button>
          ) : null}
        </Flex>

        {(mapMode === 'unit' || mapMode === 'pixel') && belowMinZoom ? (
          <Text sx={isMobile ? mobileInstructionsCSS : instructionsCSS}>
            Zoom in to
            {!isMobile ? <br /> : ' '}
            select {mapMode === 'pixel' ? 'a pixel' : 'an area'}
          </Text>
        ) : (
          <Text sx={isMobile ? mobileInstructionsCSS : instructionsCSS}>
            {mapMode === 'unit' ? (
              <>
                Select a subwatershed or marine {!isMobile ? <br /> : ' '}
                lease block to show details
                {!isMobile ? ' in sidebar' : null}
              </>
            ) : null}

            {mapMode === 'pixel' ? (
              <>
                Pan the map behind the crosshairs {!isMobile ? <br /> : ' '} to
                show details
                {!isMobile ? ' in sidebar' : null}
              </>
            ) : null}

            {mapMode === 'filter' ? (
              <>
                Select one or more indicators to filter <br /> and adjust the
                range to update the map
              </>
            ) : null}
          </Text>
        )}
      </Flex>
    </Box>
  )
}

MapModeToggle.propTypes = {
  belowMinZoom: PropTypes.bool,
  isMobile: PropTypes.bool,
}

MapModeToggle.defaultProps = {
  belowMinZoom: false,
  isMobile: false,
}

export default memo(MapModeToggle)
