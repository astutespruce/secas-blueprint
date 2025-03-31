import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import {
  Box,
  Container,
  Divider,
  Flex,
  Grid,
  Heading,
  Paragraph,
} from 'theme-ui'
import { GatsbyImage } from 'gatsby-plugin-image'

import { Layout, SEO } from 'components/layout'
import { OutboundLink } from 'components/link'
import { HeaderImage } from 'components/image'

const HelpPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
    summarizeImage: {
      childImageSharp: { gatsbyImageData: summarizeImage },
    },
    summarizeTabsImage: {
      childImageSharp: { gatsbyImageData: summarizeTabsImage },
    },
    pointDataImage: {
      childImageSharp: { gatsbyImageData: pointDataImage },
    },
    pointDataTabsImage: {
      childImageSharp: { gatsbyImageData: pointDataTabsImage },
    },
    filterImage: {
      childImageSharp: { gatsbyImageData: filterImage },
    },
    filterBeforeImage: {
      childImageSharp: { gatsbyImageData: filterBeforeImage },
    },
    filterAfterImage: {
      childImageSharp: { gatsbyImageData: filterAfterImage },
    },
    toggleLayersButtonImage: {
      childImageSharp: { gatsbyImageData: toggleLayersButtonImage },
    },
    toggleLayersModalImage: {
      childImageSharp: { gatsbyImageData: toggleLayersModalImage },
    },
    searchFieldImage: {
      childImageSharp: { gatsbyImageData: searchFieldImage },
    },
    searchOptionsImage: {
      childImageSharp: { gatsbyImageData: searchOptionsImage },
    },
    searchResultsImage: {
      childImageSharp: { gatsbyImageData: searchResultsImage },
    },
    searchLatLongImage: {
      childImageSharp: { gatsbyImageData: searchLatLongImage },
    },
    reportImage1: {
      childImageSharp: { gatsbyImageData: reportImage1 },
    },
    reportImage2: {
      childImageSharp: { gatsbyImageData: reportImage2 },
    },
    reportImage3: {
      childImageSharp: { gatsbyImageData: reportImage3 },
    },
    reportImage4: {
      childImageSharp: { gatsbyImageData: reportImage4 },
    },
    reportImage5: {
      childImageSharp: { gatsbyImageData: reportImage5 },
    },
  },
}) => (
  <Layout>
    <HeaderImage
      title="How to use this viewer"
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
        pb: '4rem',
        'h2 + p': {
          mt: '1rem',
        },
        section: {
          pb: '2rem',
        },
        'section + section': {
          mt: '4rem',
        },
        img: {
          border: '1px solid',
          borderColor: 'grey.2',
        },
      }}
    >
      <Box as="section">
        <Heading as="h2">Summarize data:</Heading>

        <Paragraph>
          This mode allows you to select a subwatershed or marine hexagon and
          view data summaries and charts for the Blueprint, indicators, threats,
          and protected areas.
        </Paragraph>

        <Grid columns={[0, 2]} gap={4} sx={{ mt: '2rem' }}>
          <Flex sx={{ flexDirection: 'column', justifyContent: 'center' }}>
            <Paragraph>
              Choose <b>Summarize data</b> from the button bar above the map.
              Click on any subwatershed or marine hexagon for details. You may
              need to zoom in to select an area.
            </Paragraph>
          </Flex>

          <Box>
            <GatsbyImage
              image={summarizeImage}
              alt="Help image showing summarize data button"
            />
          </Box>
        </Grid>

        <Grid columns={[0, '1fr 1.5fr']} gap={4} sx={{ mt: '4rem' }}>
          <Box>
            <GatsbyImage
              image={summarizeTabsImage}
              alt="Help image showing tabs in sidebar for a selected summary unit"
            />
          </Box>
          <Flex sx={{ flexDirection: 'column', justifyContent: 'center' }}>
            <Paragraph>
              Use the tabs in the sidebar to navigate the different types of
              summary information available for priorities, indicators, threats,
              and partners.
              <br />
              <br />
              <br />
              The indicators tab shows which indicators are present in the
              selected summary unit. Click on an indicator for more information
              and to see the range of values that occur that area.
            </Paragraph>
          </Flex>
        </Grid>
        <Paragraph sx={{ mt: '4rem' }}>
          You can download a detailed PDF report of the Blueprint, hubs and
          corridors, underlying indicators, and landscape-level threats for the
          selected summary unit. Click the{' '}
          <b>Export detailed maps and analysis</b> link below the area name. To
          unselect the area, click the <b>X</b> in the upper right of the
          sidebar.
        </Paragraph>
      </Box>

      <Divider />

      <Box as="section">
        <Heading as="h2">View point data:</Heading>
        <Paragraph>
          This mode allows you to show values at a specific point for the
          Blueprint, indicators, threats, and more by drilling into a single 30
          meter pixel, the smallest unit of the Blueprint analysis.
        </Paragraph>

        <Grid columns={[0, 2]} gap={4} sx={{ mt: '2rem' }}>
          <Flex sx={{ flexDirection: 'column', justifyContent: 'center' }}>
            <Paragraph>
              Choose <b>View point data</b> from the button bar above the map.
              The crosshairs in the center of the map will pinpoint a specific
              place and show details for that location in the sidebar.
              <br />
              <br />
              <br />
              You may have to zoom in for the crosshairs to appear. Zoom in
              further to choose a more precise location, especially in areas
              that are highly pixelated.
            </Paragraph>
          </Flex>
          <Box>
            <GatsbyImage
              image={pointDataImage}
              alt="Help image for view point data mode"
            />
          </Box>
        </Grid>

        <Grid columns={[0, '1fr 2fr']} gap={4} sx={{ mt: '4rem' }}>
          <Box>
            <GatsbyImage
              image={pointDataTabsImage}
              alt="Help image for view point data tabs"
            />
          </Box>
          <Flex sx={{ flexDirection: 'column', justifyContent: 'center' }}>
            <Paragraph>
              Use the tabs in the sidebar to navigate the different types of
              point-level information available for priorities, indicators,
              threats, and partners.
              <br />
              <br />
              <br />
              The indicators tab shows the pixel value for each indicator
              present at that point. Click on an indicator for more information
              about it.
            </Paragraph>
          </Flex>
        </Grid>

        <Paragraph sx={{ mt: '4rem' }}>
          Note: this approach uses pixels that have been resampled and
          reprojected for each zoom level. This means that the values shown in
          the tool may not exactly match the Blueprint and indicator data for
          that specific ground location, especially in areas of high variability
          in the data.
          <br />
          <br />
          To view and / or download more precise spatial data, please visit the{' '}
          <OutboundLink to="https://secas-fws.hub.arcgis.com/pages/blueprint">
            Blueprint page of the SECAS Atlas
          </OutboundLink>
        </Paragraph>
      </Box>

      <Divider />

      <Box as="section">
        <Heading as="h2">Filter the Blueprint:</Heading>
        <Paragraph>
          Filters can help you find the part of the Blueprint that aligns with
          your mission, interests, or specific question. Use the filters to show
          areas on the map that fall within a range of values for one or more
          layers, including the Blueprint, hubs and corridors, underlying
          indicators, and threats.
        </Paragraph>

        <Grid columns={[0, 2]} gap={4} sx={{ mt: '3rem' }}>
          <Flex sx={{ flexDirection: 'column', justifyContent: 'center' }}>
            <Paragraph>
              Choose <b>Filter the Blueprint</b> from the button bar above the
              map.
              <br />
              <br />
              <br />
              Click the checkbox for a given layer to enable it for filtering
              the map. Use the next level of checkboxes to select the specific
              values that you want to display.
            </Paragraph>
          </Flex>
          <Box>
            <GatsbyImage
              image={filterImage}
              alt="Help image for filtering the Blueprint"
            />
          </Box>
        </Grid>
        <Paragraph sx={{ mt: '4rem' }}>
          You can select more than one layer. The filters are evaluated using
          AND logic, which means that in order for a pixel to display on the
          map, it must meet all the selected criteria. If you filter by layers
          that do not co-occur at the same location, such as estuarine coastal
          condition and plays, nothing will display on the map.
        </Paragraph>
        <Grid columns={[0, 2]} gap={4} sx={{ mt: '3rem' }}>
          <Box>
            <GatsbyImage
              image={filterBeforeImage}
              alt="Help image for filtering the Blueprint showing before filters are applied"
            />
          </Box>
          <Box>
            <GatsbyImage
              image={filterAfterImage}
              alt="Help image for filtering the Blueprint showing after filters are applied"
            />
          </Box>
        </Grid>

        <Paragraph sx={{ mt: '2rem' }}>
          Note: pixel filters may take a few moments to display within your
          browser, especially as you pan or zoom the map. You may need to zoom
          in to see areas that meet your filters.
        </Paragraph>
      </Box>

      <Divider />

      <Box as="section">
        <Heading as="h2">
          Create a custom report for a specific area of interest:
        </Heading>
        <Paragraph>
          Click on the <b>Upload a shapefile</b> button in the upper right. You
          will be able to upload your area of interest and create a detailed PDF
          report of the Blueprint, hubs and corridors, underlying indicators,
          and landscape-level threats in that area.
          <br />
          <br />
          Examples of what is inside:
        </Paragraph>

        <Grid
          columns={5}
          sx={{
            mt: '1rem',
            img: {
              width: '178px',
              border: '1px solid',
              borderColor: 'grey.4',
            },
          }}
        >
          <GatsbyImage
            image={reportImage1}
            alt="Tool report example screenshot 1"
          />
          <GatsbyImage
            image={reportImage2}
            alt="Tool report example screenshot 2"
          />
          <GatsbyImage
            image={reportImage3}
            alt="Tool report example screenshot 3"
          />
          <GatsbyImage
            image={reportImage4}
            alt="Tool report example screenshot 4"
          />
          <GatsbyImage
            image={reportImage5}
            alt="Tool report example screenshot 5"
          />
        </Grid>
      </Box>

      <Divider />

      <Box as="section">
        <Heading as="h2">Display different map layers:</Heading>
        <Paragraph>
          You can display map layers other than the Blueprint. Choose{' '}
          <b>View point data</b> or <b>Filter the Blueprint</b> from the button
          bar above the map, and then click the button in the upper right of the
          map to display the list of available layers.
        </Paragraph>
        <Grid columns={[0, '1.5fr 1fr']} gap={4} sx={{ mt: '3rem' }}>
          <Box>
            <GatsbyImage
              image={toggleLayersButtonImage}
              alt="Help image for toggle layers button"
            />
          </Box>
          <Box>
            <GatsbyImage
              image={toggleLayersModalImage}
              alt="Help image for toggle layers modal popup"
            />
          </Box>
        </Grid>
      </Box>

      <Divider />

      <Box as="section">
        <Heading as="h2">Find a specific location:</Heading>
        <Paragraph>
          You can use the search bar in the upper right of the map to search by
          place name, address, or latitude and longitude coordinates.
        </Paragraph>
        <Grid columns={[0, '2fr 1fr 1.5fr']} gap={4} sx={{ mt: '2rem' }}>
          <Flex sx={{ flexDirection: 'column', justifyContent: 'center' }}>
            <Paragraph>
              Click in the search field to expand it. Use the dropdown on the
              left of the search bar to switch between search by placename and
              search by latitude and longitude.
            </Paragraph>
          </Flex>
          <Box>
            <GatsbyImage
              image={searchFieldImage}
              alt="Help image for search field"
            />
          </Box>
          <Box>
            <GatsbyImage
              image={searchOptionsImage}
              alt="Help image for search field options"
            />
          </Box>
        </Grid>

        <Grid columns={[0, 3]} gap={4} sx={{ mt: '4rem' }}>
          <Flex sx={{ flexDirection: 'column', justifyContent: 'center' }}>
            <Paragraph>
              You can search by place name or address, or enter latitude and
              longitude coordinates directly.
              <br />
              <br />
              Once you have selected a location from the list of results, or
              clicked the <b>Go</b> button for latitude and longitude, it will
              show a marker at that location on the map.
            </Paragraph>
          </Flex>
          <Box>
            <GatsbyImage
              image={searchResultsImage}
              alt="Help image for search results for placename search"
            />
          </Box>

          <Box>
            <GatsbyImage
              image={searchLatLongImage}
              alt="Help image for latitude / longitude search"
            />
          </Box>
        </Grid>
        <Paragraph sx={{ mt: '2rem' }}>
          To remove the marker, click the <b>X</b> in the search field to clear
          the search.
        </Paragraph>
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
    summarizeImage: file(relativePath: { eq: "help-summarize.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 600
        )
      }
    }
    summarizeTabsImage: file(relativePath: { eq: "help-summarize-tabs.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 600
        )
      }
    }
    pointDataImage: file(relativePath: { eq: "help-point-data.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 600
        )
      }
    }
    pointDataTabsImage: file(relativePath: { eq: "help-point-data-tabs.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 600
        )
      }
    }
    filterImage: file(relativePath: { eq: "help-filter.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 600
        )
      }
    }
    filterBeforeImage: file(relativePath: { eq: "help-filter-before.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 600
        )
      }
    }
    filterAfterImage: file(relativePath: { eq: "help-filter-after.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 600
        )
      }
    }
    toggleLayersButtonImage: file(
      relativePath: { eq: "help-toggle-layers-button.png" }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 600
        )
      }
    }
    toggleLayersModalImage: file(
      relativePath: { eq: "help-toggle-layers-modal.png" }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 600
        )
      }
    }
    searchFieldImage: file(relativePath: { eq: "help-search-field.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 600
        )
      }
    }
    searchOptionsImage: file(relativePath: { eq: "help-search-options.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 600
        )
      }
    }
    searchResultsImage: file(relativePath: { eq: "help-search-results.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 600
        )
      }
    }
    searchLatLongImage: file(relativePath: { eq: "help-search-lat-long.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 600
        )
      }
    }
    reportImage1: file(relativePath: { eq: "report/report_sm_1.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 180
        )
      }
    }
    reportImage2: file(relativePath: { eq: "report/report_sm_2.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 180
        )
      }
    }
    reportImage3: file(relativePath: { eq: "report/report_sm_3.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 180
        )
      }
    }
    reportImage4: file(relativePath: { eq: "report/report_sm_4.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 180
        )
      }
    }
    reportImage5: file(relativePath: { eq: "report/report_sm_5.png" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          formats: [AUTO, WEBP]
          placeholder: BLURRED
          width: 180
        )
      }
    }
  }
`

HelpPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
    summarizeImage: PropTypes.object.isRequired,
    summarizeTabsImage: PropTypes.object.isRequired,
    pointDataImage: PropTypes.object.isRequired,
    pointDataTabsImage: PropTypes.object.isRequired,
    filterImage: PropTypes.object.isRequired,
    filterBeforeImage: PropTypes.object.isRequired,
    filterAfterImage: PropTypes.object.isRequired,
    toggleLayersButtonImage: PropTypes.object.isRequired,
    toggleLayersModalImage: PropTypes.object.isRequired,
    searchFieldImage: PropTypes.object.isRequired,
    searchOptionsImage: PropTypes.object.isRequired,
    searchResultsImage: PropTypes.object.isRequired,
    searchLatLongImage: PropTypes.object.isRequired,
    reportImage1: PropTypes.object.isRequired,
    reportImage2: PropTypes.object.isRequired,
    reportImage3: PropTypes.object.isRequired,
    reportImage4: PropTypes.object.isRequired,
    reportImage5: PropTypes.object.isRequired,
  }).isRequired,
}

export default HelpPage

export const Head = () => <SEO title="How to use the Blueprint Explorer" />
