import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'

import { Layout, SEO } from 'components/layout'
import { HeaderImage } from 'components/image'
import { UploadContainer } from 'components/report'

const CustomReportPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
  },
}) => (
  <Layout>
    <HeaderImage
      title="Create a custom Blueprint report"
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

    <UploadContainer />
  </Layout>
)

export const pageQuery = graphql`
  query CustomReportPageQuery {
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

CustomReportPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export default CustomReportPage

export const Head = () => <SEO title="Create a Custom Blueprint Report" />
