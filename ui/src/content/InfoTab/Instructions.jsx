import React from 'react'
import { Box, Heading } from 'theme-ui'

const MobileInstructions = () => (
  <>
    <Heading as="h4" sx={{ mb: '0.5rem' }}>
      Subwatershed and marine lease block details:
    </Heading>
    <p>
      Use the <b>Map</b> tab to explore the Blueprint across the Southeast
      region. Zoom in to show boundaries of subwatersheds or marine lease blocks
      that you can tap for more information.
      <br />
      <br />
      Use the tabs at the bottom of the screen to navigate the different types
      of summary information available.
      <br />
      <br />
      On the Indicators tab, you can see the average value for each indicator
      present in that area.
      <br />
      <br />
      {/* TODO: */}
      {/* To unselect the area, click on the{" "}
      <ResetIcon style={{ marginBottom: "-0.5em", fill: "#666" }} /> button in
      the upper right or click on the unit again in the map. */}
    </p>

    <Heading as="h4">To find a specific area:</Heading>
    <p>
      Use the <b>Find location</b> tab to search for a place by name. When you
      tap on a place to select it from the list, it will show a marker at that
      location on the map.
    </p>
  </>
)

const DesktopInstructions = () => (
  <>
    <Heading as="h4">Subwatershed and marine lease block details:</Heading>
    <p>
      Use the map to explore the Blueprint across the Southeast region. Zoom in
      to show boundaries of subwatersheds or marine lease blocks that you can
      click on for more information.
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
      {/* TODO: */}
      {/* To unselect the area, click on the{" "}
      <ResetIcon style={{ marginBottom: "-0.5em", fill: "#666" }} /> button in
      the upper right of the sidebar. */}
    </p>
    <Heading as="h4">Map tools:</Heading>
    <p>
      Hover over one of the tool buttons on the right side of the map for more
      information.
    </p>
    <ul>
      <li>
        <b>Zoom to specific area:</b> enable this tool and then draw a box on
        the map to zoom in.
      </li>
      <li>
        <b>Search by location name:</b> click on this tool to enter a place name
        to search for. It will show a marker on the map when you select a place
        from the list.
      </li>
      <li>
        <b>Zoom to my location:</b> click on this tool to zoom the map to your
        current physical location, using location services in your device. Your
        browser may prompt you for permission.
      </li>
      <li>
        <b>View pixel-level details:</b> enable this tool to view details at the
        pixel level for the Blueprint (for advanced users). Details for the
        pixel under the crosshairs in the center of the map will show in the
        sidebar, and will update as you pan or zoom the map.
      </li>
    </ul>
  </>
)

const Instructions = () => {
  const isMobile = false // TODO

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
