import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box } from 'theme-ui'

import { HeaderImage } from 'components/image'
import { Layout, SEO } from 'components/layout'
import { OutboundLink } from 'components/link'
import { hasWindow } from 'util/dom'

const NotFoundPage = ({
  data: {
    image: {
      childImageSharp: { gatsbyImageData: image },
    },
  },
}) => {
  if (!hasWindow) {
    // prevents initial load of this page for client routes
    return null
  }

  return (
    <Layout>
      <Box sx={{ position: 'relative', height: '100%' }}>
        <HeaderImage
          image={image}
          title="PAGE NOT FOUND"
          subtitle="Sorry, we could not find what you were looking for here."
          height="100%"
          minHeight="100%"
          maxHeight="100%"
        />
        <Box
          author="G. Peeples / U.S. Fish and Wildlife Service Southeast Region"
          url="https://flickr.com/photos/usfwssoutheast/48754428566/"
          sx={{
            zIndex: 100,
            bg: 'rgba(0, 0, 0, 0.6)',
            py: '0.25rem',
            px: '1rem',
            color: '#FFF',
            position: 'absolute',
            bottom: 0,
            right: 0,
            '& a': {
              color: '#FFF',
            },
          }}
        >
          <Box
            sx={{
              fontSize: 'smaller',
              textAlign: 'right',
              color: '#FFF',
              a: {
                color: '#FFF',
                textDecoration: 'none',
              },
            }}
          >
            Photo:&nbsp;
            <OutboundLink to="https://flickr.com/photos/usfwssoutheast/48754428566/">
              G. Peeples / U.S. Fish and Wildlife Service Southeast Region
            </OutboundLink>
          </Box>
        </Box>
      </Box>
    </Layout>
  )
}

// image: https://flickr.com/photos/usfwssoutheast/48754428566/
export const pageQuery = graphql`
  query NotFoundPageQuery {
    image: file(relativePath: { eq: "48754428566_d34b348ac3_o.jpg" }) {
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

NotFoundPage.propTypes = {
  data: PropTypes.shape({
    image: PropTypes.object.isRequired,
  }).isRequired,
}

export default NotFoundPage

export const Head = () => <SEO title="Not Found" />
