import React from 'react'
import { Box, Heading, Paragraph } from 'theme-ui'
import { TimesCircle } from '@emotion-icons/fa-regular'
import { LayerGroup } from '@emotion-icons/fa-solid'

import { useBreakpoints } from 'components/layout'
import { OutboundLink } from 'components/link'

const CloseButton = () => (
  <Box
    as="span"
    sx={{
      color: 'grey.8',
    }}
  >
    <TimesCircle size="1em" style={{ marginTop: '-4px' }} />
  </Box>
)

const MobileInstructions = () => (
  <>
    <Heading as="h4" sx={{ mt: '2rem' }}>
      Subwatershed and marine lease block details:
    </Heading>
    <Paragraph sx={{ mt: '0.25rem' }}>
      Choose <b>Summary data</b> from the button bar below the map. Click on any
      subwatershed or marine lease block for details. You may need to zoom in
      futher to select an area.
      <br />
      <br />
      Use the tabs in the bottom bar to navigate the different types of summary
      information available.
      <br />
      <br />
      On the indicators tab, you can see which indicators are present in that
      area. Click on an indicator for more information and to see the range of
      values that occur there.
      <br />
      <br />
      To unselect the area, click on the <CloseButton /> button in the top bar.
    </Paragraph>

    <Heading as="h4" sx={{ mt: '2rem' }}>
      Pixel-level details:
    </Heading>
    <Paragraph sx={{ mt: '0.25rem' }}>
      Choose <b>Pixel data</b> from the button bar below the map. Tap on any
      location in the map to show pixel-level data for that location. You may
      need to zoom in further to select pixels. Zoom in further to choose a more
      precise location, especially in areas that are highly pixelated.
      <br />
      <br />
      Use the tabs in the bottom bar to navigate the different types of
      information available.
      <br />
      <br />
      On the Indicators tab, you can see the pixel value for each indicator
      present at that location. Click on an indicator for more information about
      it.
      <br />
      <br />
      Note: this approach uses pixels that have been resampled and reprojected
      for each zoom level. This means that the values shown in the tool may not
      exactly match the Blueprint and indicator data for that specific ground
      location, especially in areas of high variability in the data.
      <br />
      <br />
      To unselect the pixel, click on the <CloseButton /> button in top bar.
    </Paragraph>

    <Heading as="h4" sx={{ mt: '2rem' }}>
      To find a specific area:
    </Heading>
    <Paragraph sx={{ mt: '0.25rem' }}>
      Use the <b>Find Location</b> tab at the bottom to search for a place by
      name. When you tap on a place to select it from the list, it will show a
      marker at that location on the map.
    </Paragraph>
  </>
)

const DesktopInstructions = () => (
  <>
    <Heading as="h4" sx={{ mt: '1rem' }}>
      Subwatershed and marine lease block details:
    </Heading>
    <Paragraph sx={{ mt: '0.25rem' }}>
      Choose <b>Summary data</b> from the button bar above the map. Click on any
      subwatershed or marine lease block for details. You may need to zoom in
      futher to select an area.
      <br />
      <br />
      Use the tabs in the sidebar to navigate the different types of summary
      information available.
      <br />
      <br />
      On the indicators tab, you can see which indicators are present in that
      area. Click on an indicator for more information and to see the range of
      values that occur there.
      <br />
      <br />
      You can download a detailed PDF report of the Blueprint, underlying
      indicators, and landscape-level threats for your area of interest. Click
      the &quot;Export detailed maps and analysis&quot; link below the area
      name.
      <br />
      <br />
      To unselect the area, click on the <CloseButton /> button in the upper
      right of the sidebar.
    </Paragraph>

    <Heading as="h4" sx={{ mt: '2rem' }}>
      Pixel-level details:
    </Heading>
    <Paragraph sx={{ mt: '0.25rem' }}>
      Choose <b>Pixel data</b> from the button bar above the map. Click on any
      location to show pixel-level data for that location. You may need to zoom
      in further to select pixels. Zoom in further to choose a more precise
      location, especially in areas that are highly pixelated.
      <br />
      <br />
      Use the tabs in the sidebar to navigate the different types of summary
      information available.
      <br />
      <br />
      On the Indicators tab, you can see the pixel value for each indicator
      present at that location. Click on an indicator for more information about
      it.
      <br />
      <br />
      Note: this approach uses pixels that have been resampled and reprojected
      for each zoom level. This means that the values shown in the tool may not
      exactly match the Blueprint and indicator data for that specific ground
      location, especially in areas of high variability in the data. To view and
      / or download more precise spatial data, please visit the{' '}
      <OutboundLink to="https://secas-fws.hub.arcgis.com/pages/blueprint">
        Blueprint page of the SECAS Atlas
      </OutboundLink>
      .
    </Paragraph>

    <Heading as="h4" sx={{ mt: '2rem' }}>
      Pixel-level filtering:
    </Heading>
    <Paragraph sx={{ mt: '0.25rem' }}>
      Pixel filters allow you to show areas in the map that fall within a range
      of values for one or more map layers, including the Blueprint and
      indicators.
      <br />
      <br />
      Choose <b>Pixel filters</b> from the button bar above the map. Click on
      the checkbox for a given map layer to enable that layer for filtering the
      map. Use the range slider to select the range of values that you want to
      display on the map. You may need to zoom in on the map to see areas that
      meet your filters.
      <br />
      <br />
      You can select more than one map layer. The filters are evaluating using
      AND logic, which means that in order for a pixel to display on the map,
      every map layer that you enable must fall within the range of values you
      have selected. If you use filters for map layers that do not co-occur at
      the same location, such as South Atlantic marine mammals and Great Plains
      perennial grasslands, nothing will display on the map.
      <br />
      <br />
      Pixel filters are more resource intensive, and may take a few moments to
      display within your browser, especially as you pan or zoom the map.
    </Paragraph>

    <Heading as="h4" sx={{ mt: '2rem' }}>
      To display different map layers:
    </Heading>
    <Paragraph sx={{ mt: '0.25rem' }}>
      You can display map layers other than the Blueprint. Choose{' '}
      <b>Pixel data</b> or <b>Pixel filters</b> from the button bar above the
      map, and then click on the
      <Box sx={{ display: 'inline', mx: '0.5rem' }}>
        <LayerGroup size="1em" />
      </Box>
      button in the upper right of the map to display the list of available map
      layers.
    </Paragraph>

    <Heading as="h4" sx={{ mt: '2rem' }}>
      To create a custom report for a specific area of interest:
    </Heading>
    <Paragraph sx={{ mt: '0.25rem' }}>
      Click on the &quot;Upload Shapefile&quot; button in the upper right. You
      will be able to upload your area of interest and create a detailed PDF
      report of the Blueprint, underlying indicators, and landscape-level
      threats for this summary area.
    </Paragraph>

    <Heading as="h4" sx={{ mt: '2rem' }}>
      To find a specific area:
    </Heading>
    <Paragraph sx={{ mt: '0.25rem' }}>
      Use the <b>Find Location</b> tab in the sidebar to search for a place by
      name. When you tap on a place to select it from the list, it will show a
      marker at that location on the map.
    </Paragraph>
  </>
)

const Instructions = () => {
  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

  return (
    <Box as="section" sx={{ mt: '2rem' }}>
      <Heading as="h1" sx={{ mb: '0.5rem', fontSize: [4, 5] }}>
        How To Use This Viewer
      </Heading>

      {isMobile ? <MobileInstructions /> : <DesktopInstructions />}
    </Box>
  )
}

export default Instructions
