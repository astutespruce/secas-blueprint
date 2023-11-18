import React from 'react'
import { Box, Heading, Paragraph, Divider } from 'theme-ui'
import { TimesCircle } from '@emotion-icons/fa-regular'

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

const Instructions = () => (
  <>
    <Divider />
    <Box as="section" sx={{ mt: '2rem' }}>
      <Heading as="h2" sx={{ mb: '0.5rem', fontSize: [4, 5] }}>
        How To Use This Viewer
      </Heading>

      <Heading as="h3" sx={{ mt: '2rem', fontSize: [2, 3] }}>
        Subwatershed and marine hexagon details:
      </Heading>
      <Paragraph sx={{ mt: '0.25rem' }}>
        Choose <b>Summary data</b> from the button bar below the map. Click on
        any subwatershed or marine hexagon for details. You may need to zoom in
        futher to select an area.
        <br />
        <br />
        Use the tabs in the bottom bar to navigate the different types of
        summary information available.
        <br />
        <br />
        On the indicators tab, you can see which indicators are present in that
        area. Click on an indicator for more information and to see the range of
        values that occur there.
        <br />
        <br />
        To unselect the area, click on the <CloseButton /> button in the top
        bar.
      </Paragraph>

      <Heading as="h3" sx={{ mt: '2rem', fontSize: [2, 3] }}>
        Pixel-level details:
      </Heading>
      <Paragraph sx={{ mt: '0.25rem' }}>
        Choose <b>View point data</b> from the button bar below the map. The
        crosshairs in the center of the map will pinpoint a specific place and
        show details for that location in the sidebar. You may have to zoom in
        for the crosshairs to appear. Zoom in further to choose a more precise
        location, especially in areas that are highly pixelated.
        <br />
        <br />
        Use the tabs in the bottom bar to navigate the different types of
        point-level information available for priorities, indicators, threats,
        and partners.
        <br />
        <br />
        The indicators tab shows the pixel value for each indicator present at
        that point. Click on an indicator for more information about it.
        <br />
        <br />
        Note: this approach uses pixels that have been resampled and reprojected
        for each zoom level. This means that the values shown in the tool may
        not exactly match the Blueprint and indicator data for that specific
        ground location, especially in areas of high variability in the data. To
        view and / or download more precise spatial data, please visit the{' '}
        <OutboundLink to="https://secas-fws.hub.arcgis.com/pages/blueprint">
          Blueprint page of the SECAS Atlas
        </OutboundLink>
        <br />
        <br />
        To unselect the pixel, click on the <CloseButton /> button in top bar.
      </Paragraph>

      <Heading as="h3" sx={{ mt: '2rem', fontSize: [2, 3] }}>
        To find a specific area:
      </Heading>
      <Paragraph sx={{ mt: '0.25rem' }}>
        Use the <b>Find Location</b> tab at the bottom to search for a place by
        name. When you tap on a place to select it from the list, it will show a
        marker at that location on the map.
        <br />
        You can also choose to add a marker at your current location (if allowed
        by your device).
      </Paragraph>
    </Box>
  </>
)

export default Instructions
