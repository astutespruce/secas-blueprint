import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Container, Flex, Grid, Heading, Paragraph, Text } from 'theme-ui'

import { Layout, SEO } from 'components/layout'
import { OutboundLink } from 'components/link'
import { HeaderImage } from 'components/image'

const HelpPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
  },
}) => (
  <Layout>
    <HeaderImage
      title="How To Use This Viewer"
      image={headerImage}
      credits={{
        author: 'U.S. Fish and Wildlife Service Southeast Region',
        url: 'https://www.flickr.com/photos/usfwssoutheast/26871026541/',
      }}
      caption="Black Skimmers"
      height="14rem"
      maxHeight="14rem"
      minHeight="14rem"
    />

    <Container
      sx={{
        'h2 + p': {
          mt: '0.25rem',
          borderTop: '1px solid',
          borderTopColor: 'grey.1',
          pt: '0.5rem',
        },
        'section + section': {
          mt: '4rem',
        },
      }}
    >
      <Box as="section">
        <Heading as="h2">Summarize data:</Heading>

        <Paragraph>
          This mode allows you to select a subwatershed or marine lease block
          and view data summaries and charts for the Blueprint, indicators,
          threats, and land ownership.
          <br />
          <br />
          Choose <b>Summarize data</b> from the button bar above the map. Click
          on any subwatershed or marine lease block for details. You may need to
          zoom in to select an area.
          <br />
          <br />
          Use the tabs in the sidebar to navigate the different types of summary
          information available for priorities, indicators, threats, and
          partners.
          <br />
          <br />
          The indicator tab shows which indicators are present in the selected
          summary unit. Click on an indicator for more information and to see
          the range of values that occur that area.
          <br />
          <br />
          You can download a detailed PDF report of the Blueprint, hubs and
          corridors, underlying indicators, and landscape-level threats for the
          selected summary unit. Click the{' '}
          <b>Export detailed maps and analysis</b> link below the area name. To
          unselect the area, click the <b>X</b> in the upper right of the
          sidebar.
        </Paragraph>
      </Box>

      <Box as="section">
        <Heading as="h2">View point data:</Heading>
        <Paragraph>
          This mode allows you to show values at a specific point for the
          Blueprint, indicators, threats, and more by drilling into a single 30
          m pixel, the smallest unit of the Blueprint analysis.
          <br />
          <br />
          Choose <b>View point data</b> from the button bar above the map. The
          crosshairs in the center of the map will pinpoint a specific place and
          show details for that location in the sidebar. You may have to zoom in
          for the crosshairs to appear. Zoom in further to choose a more precise
          location, especially in areas that are highly pixelated.
          <br />
          <br />
          Use the tabs in the sidebar to navigate the different types of
          point-level information available for priorities, indicators, threats,
          and partners.
          <br />
          <br />
          The indicators tab shows the pixel value for each indicator present at
          that point. Click on an indicator for more information about it.
          <br />
          <br />
          Note: this approach uses pixels that have been resampled and
          reprojected for each zoom level. This means that the values shown in
          the tool may not exactly match the Blueprint and indicator data for
          that specific ground location, especially in areas of high variability
          in the data. To view and / or download more precise spatial data,
          please visit the{' '}
          <OutboundLink to="https://secas-fws.hub.arcgis.com/pages/blueprint">
            Blueprint page of the SECAS Atlas
          </OutboundLink>
          .
        </Paragraph>
      </Box>

      <Box as="section">
        <Heading as="h2">Filter the Blueprint:</Heading>
        <Paragraph>
          Pixel filters can help you find the part of the Blueprint that aligns
          with your mission, interests, or specific question. Use the filters to
          show areas on the map that fall within a range of values for one or
          more layers, including the Blueprint, hubs and corridors, underlying
          indicators, and threats.
          <br />
          <br />
          Choose <b>Filter the Blueprint</b> from the button bar above the map.
          Click the checkbox for a given layer to enable it for filtering the
          map. Use the next level of checkboxes to select the specific values
          that you want to display. You may need to zoom in to see areas that
          meet your filters.
          <br />
          <br />
          You can select more than one layer. The filters are evaluated using
          AND logic, which means that in order for a pixel to display on the
          map, it must meet all the selected criteria. If you filter by layers
          that do not co-occur at the same location, such as estuarine coastal
          condition and Great Plains perennial grasslands, nothing will display
          on the map.
          <br />
          <br />
          Pixel filters may take a few moments to display within your browser,
          especially as you pan or zoom the map.
        </Paragraph>
      </Box>

      <Box as="section">
        <Heading as="h2">Display different map layers:</Heading>
        <Paragraph>
          You can display map layers other than the Blueprint. Choose{' '}
          <b>View point data</b> or <b>Filter the Blueprint</b> from the button
          bar above the map, and then click the button in the upper right of the
          map to display the list of available layers.
        </Paragraph>
      </Box>

      <Box as="section">
        <Heading as="h2">
          Create a custom report for a specific area of interest:
        </Heading>
        <Paragraph>
          Click on the <b>Upload Shapefile</b> button in the upper right. You
          will be able to upload your area of interest and create a detailed PDF
          report of the Blueprint, hubs and corridors, underlying indicators,
          and landscape-level threats in that area.
        </Paragraph>
      </Box>

      <Box as="section">
        <Heading as="h2">Find a specific location:</Heading>
        <Paragraph>
          Use the search bar in the upper right of the map. You can search by
          place name or address, or enter latitude and longitude coordinates
          directly. Once you have selected a location, it will show a marker at
          that location on the map. To remove the marker, click the <b>X</b> in
          the search field to clear the search.
        </Paragraph>
        X
      </Box>
    </Container>
  </Layout>
)

export const pageQuery = graphql`
  query HelpPageQuery {
    headerImage: file(relativePath: { eq: "26871026541_48a8096dd9_o.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: FULL_WIDTH
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
  }
`

HelpPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export default HelpPage

export const Head = () => <SEO title="How to use the Blueprint Explorer" />
