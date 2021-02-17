import React from 'react'
import { Box, Button, Heading, Text } from 'theme-ui'
import { TimesCircle } from '@emotion-icons/fa-regular'

import { useBreakpoints } from 'components/layout'

const CloseButton = () => (
  <Button
    variant="close"
    sx={{ margin: 0, padding: 0, flex: '0 0 auto', color: 'grey.8' }}
  >
    {' '}
    <TimesCircle size="1em" />
  </Button>
)

const MobileInstructions = () => (
  <>
    {/* <Heading as="h4">Pixel-level details:</Heading>
    <Text as="p" sx={{ mt: '0.25rem' }}>
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
    </Text> */}

    <Heading as="h4" sx={{ mt: '2rem' }}>
      Subwatershed and marine lease block details:
    </Heading>
    <Text as="p" sx={{ mt: '0.25rem' }}>
      Choose <b>Summary data</b> from the button bar below the map. Click on any
      subwatershed or marine lease block for details. You may need to zoom in
      futher to select an area.
      <br />
      <br />
      Use the tabs in the bottom bar to navigate the different types of summary
      information available.
      <br />
      <br />
      On the Indicators tab, you can see the average value for each indicator
      present in that area. Click on an indicator for more information about it.
      <br />
      <br />
      To unselect the area, click on the <CloseButton /> button in the top bar.
    </Text>

    <Heading as="h4" sx={{ mt: '2rem' }}>
      To find a specific area:
    </Heading>
    <Text as="p" sx={{ mt: '0.25rem' }}>
      Use the <b>Find Location</b> tab at the bottom to search for a place by
      name. When you tap on a place to select it from the list, it will show a
      marker at that location on the map.
    </Text>
  </>
)

const DesktopInstructions = () => (
  <>
    {/* <Heading as="h4">Pixel-level details:</Heading>
    <Text as="p" sx={{ mt: '0.25rem' }}>
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
      / or download more precise spatial data, please visit{' '}
      <OutboundLink to="https://seregion.databasin.org/galleries/5d5eb2989ea14a9f8df3ebb619fe470c/">
        the Blueprint Gallery
      </OutboundLink>{' '}
      on the Conservation Planning Atlas.
      <br />
      <br />
      To unselect the pixel, click on the <CloseButton /> button in the upper
      right of the sidebar.
    </Text> */}

    <Heading as="h4" sx={{ mt: '2rem' }}>
      Subwatershed and marine lease block details:
    </Heading>
    <Text as="p" sx={{ mt: '0.25rem' }}>
      Choose <b>Summary data</b> from the button bar above the map. Click on any
      subwatershed or marine lease block for details. You may need to zoom in
      futher to select an area.
      <br />
      <br />
      Use the tabs in the sidebar to navigate the different types of summary
      information available.
      <br />
      <br />
      On the Indicators tab, you can see the average value for each indicator
      present in that area. Click on an indicator for more information about it.
      <br />
      <br />
      You can download a detailed PDF report of the Blueprint, underlying
      indicators, and landscape-level threats for your area of interest. Click
      the &quot;Create summary report&quot; link below the area name.
      <br />
      <br />
      To unselect the area, click on the <CloseButton /> button in the upper
      right of the sidebar.
    </Text>

    <Heading as="h4" sx={{ mt: '2rem' }}>
      To create a custom report for a specific area of interest:
    </Heading>
    <Text as="p" sx={{ mt: '0.25rem' }}>
      Click on the &quot;Custom Report&quot; button in the upper right. You will
      be able to upload your area of interest and create a detailed PDF report
      of the Blueprint, underlying indicators, and landscape-level threats for
      this summary area.
    </Text>

    <Heading as="h4" sx={{ mt: '2rem' }}>
      To find a specific area:
    </Heading>
    <Text as="p" sx={{ mt: '0.25rem' }}>
      Use the <b>Find Location</b> tab in the sidebar to search for a place by
      name. When you tap on a place to select it from the list, it will show a
      marker at that location on the map.
    </Text>
  </>
)

const Instructions = () => {
  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0

  return (
    <Box as="section" sx={{ mt: '2rem' }}>
      <Heading as="h3" sx={{ mb: '0.5rem' }}>
        How To Use This Viewer
      </Heading>

      {isMobile ? <MobileInstructions /> : <DesktopInstructions />}
    </Box>
  )
}

export default Instructions
