import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Flex } from 'theme-ui'
import styled from '@emotion/styled'
import BackgroundImage from 'gatsby-background-image'
import { graphql } from 'gatsby'

import { Layout } from 'components/layout'

const Image = styled(BackgroundImage)`
  height: 100%;
  background-position: top center !important;
`

const NotFoundPage = ({ data: { image } }) => (
  <Layout title="404: Not found">
    <Image Tag="div" fluid={image.childImageSharp.fluid}>
      <Flex
        sx={{
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          height: '100%',
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
    </Image>
  </Layout>
)

// image: https://unsplash.com/photos/gAvQfrHwbgY

export const pageQuery = graphql`
  query NotFoundPageQuery {
    image: file(relativePath: { eq: "jack-kelly-gAvQfrHwbgY-unsplash.jpg" }) {
      childImageSharp {
        fluid(maxWidth: 3200) {
          ...GatsbyImageSharpFluid_withWebp
        }
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
