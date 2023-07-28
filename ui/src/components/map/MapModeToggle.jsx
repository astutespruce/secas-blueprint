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
              content="Show data summaries and charts for a subwatershed or marine lease block"
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
              content="Show values at a specific point for the Blueprint, indicators, threats, and more"
              direction="bottom"
              maxWidth="240px"
              fontSize={0}
            >
              View point data
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
                content="Find your part of the Blueprint by showing only areas that score within a certain range on indicators and more"
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
            select {mapMode === 'pixel' ? 'a point' : 'an area'}
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
