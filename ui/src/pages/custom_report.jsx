import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'

import { Layout } from 'components/layout'
import { BannerImage } from 'components/image'
import { UploadContainer } from 'components/report'

const CustomReportPage = ({ data: { headerImage } }) => (
  <Layout title="Create a Custom Blueprint Report">
    <BannerImage
      title="Create a Custom Blueprint Report"
      src={headerImage}
      url="https://www.flickr.com/photos/usfwssoutheast/26871026541/"
      credit="U.S. Fish and Wildlife Service Southeast Region"
      caption="Black Skimmers"
      height="10rem"
      maxHeight="10rem"
    />

    <UploadContainer />
  </Layout>
)

export const pageQuery = graphql`
  query CustomReportPageQuery {
    headerImage: file(relativePath: { eq: "26871026541_48a8096dd9_o.jpg" }) {
      childImageSharp {
        fluid(maxWidth: 3200) {
          ...GatsbyImageSharpFluid_withWebp
        }
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
