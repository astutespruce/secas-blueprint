import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { Box, Flex, Heading } from 'theme-ui'
import { convertToBgImage } from 'gbimage-bridge'
import BackgroundImage from 'gatsby-background-image'

import { Layout } from 'components/layout'
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
    <Layout title="404: Not found">
      <BackgroundImage
        {...convertToBgImage(image)}
        style={{
          height: '100%',
        }}
        alt=""
        preserveStackingContext
      >
        <Flex
          sx={{
            justifyContent: 'center',
            alignItems: 'center',
            flexDirection: 'column',
            height: '100%',
            flex: '1 1 auto',
            px: '1rem',
          }}
        >
          <Box
            sx={{
              color: '#FFF',
              p: '3rem',
              background: 'rgba(0,0,0,0.7)',
            }}
          >
            <Heading as="h1">NOT FOUND</Heading>
            <Heading as="h2">
              Sorry, we could not find what you were looking for here.
            </Heading>
          </Box>
        </Flex>
      </BackgroundImage>
    </Layout>
  )
}

// image: https://unsplash.com/photos/gAvQfrHwbgY

export const pageQuery = graphql`
  query NotFoundPageQuery {
    image: file(relativePath: { eq: "jack-kelly-gAvQfrHwbgY-unsplash.jpg" }) {
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
