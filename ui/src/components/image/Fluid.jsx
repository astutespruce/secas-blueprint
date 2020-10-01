import React from 'react'
import PropTypes from 'prop-types'
import Img from 'gatsby-image'
import styled from '@emotion/styled'
import { Box, Flex, Heading } from 'theme-ui'

import ImageCredits from './ImageCredits'

const StyledImage = styled(Img)`
  position: absolute !important;
  bottom: 0;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1;
`

const Fluid = ({
  image,
  height,
  minHeight,
  maxHeight,
  title,
  credits,
  caption,
}) => (
  <>
    <Box
      sx={{
        height,
        minHeight,
        maxHeight: maxHeight || height,
        mt: 0,
        overflow: 'hidden',
        width: '100%',
        position: 'relative',
        zIndex: 0,
      }}
    >
      <StyledImage fluid={image} />

      {title && (
        <Flex
          sx={{
            justifyContent: 'center',
            alignItems: 'flex-end',
            position: 'absolute',
            zIndex: 2,
            top: 0,
            bottom: 0,
            left: 0,
            right: 0,
            color: '#FFF',
            background: 'linear-gradient(transparent 0%, #0000009c 30%)',
          }}
        >
          <Heading
            as="h1"
            sx={{
              padding: '3rem 1rem',
              margin: 0,
            }}
          >
            {title}
          </Heading>
        </Flex>
      )}
    </Box>
    {credits ? (
      <ImageCredits>
        {caption ? `${caption} | ` : null}
        Photo:&nbsp;
        <a href={credits.url} target="_blank" rel="noopener noreferrer">
          {credits.author}
        </a>
      </ImageCredits>
    ) : null}
  </>
)

Fluid.propTypes = {
  image: PropTypes.any.isRequired,
  height: PropTypes.string,
  minHeight: PropTypes.string,
  maxHeight: PropTypes.string,
  title: PropTypes.string,
  credits: PropTypes.shape({
    url: PropTypes.string.isRequired,
    author: PropTypes.string.isRequired,
  }),
  caption: PropTypes.string,
}

Fluid.defaultProps = {
  height: '60vh',
  minHeight: '20rem',
  maxHeight: null,
  title: null,
  credits: null,
  caption: null,
}

export default Fluid
