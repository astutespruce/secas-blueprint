import React from 'react'
import PropTypes from 'prop-types'
import { Box, Container, Heading } from 'theme-ui'
import { GatsbyImage } from 'gatsby-plugin-image'

import Credits from './Credits'

const HeaderImage = ({
  image,
  height,
  minHeight,
  maxHeight,
  title,
  subtitle,
  credits,
  caption,
  background,
}) => (
  <Box
    sx={{
      position: 'relative',
      height,
      minHeight,
      maxHeight: maxHeight || height,
    }}
  >
    <GatsbyImage
      image={image}
      style={{
        position: 'relative',
        top: 0,
        zIndex: 0,
        height,
        minHeight,
        maxHeight: maxHeight || height,
      }}
      alt=""
    />

    <Box
      sx={{
        mt: 0,
        overflow: 'hidden',
        width: '100%',
        position: 'absolute',
        zIndex: 2,
        top: 0,
        bottom: 0,
        left: 0,
        right: 0,
      }}
    >
      {title && (
        <Box
          sx={{
            background,
            height: '100%',
            py: ['2rem', '3rem'],
          }}
        >
          <Container
            sx={{
              p: '1rem',
            }}
          >
            <Heading
              as="h1"
              sx={{
                m: 0,
                color: '#FFF',
                textShadow: '1px 1px 3px #000',
                lineHeight: 1.1,
                fontSize: ['3rem', '3rem', '4rem'],
              }}
            >
              {title}
            </Heading>

            {subtitle && (
              <Heading
                as="h2"
                sx={{
                  margin: '0.5rem 0 0 0',
                  fontWeight: 'normal',
                  fontSize: '1.75rem',
                  textShadow: '1px 1px 3px #000',
                  color: '#FFF',
                }}
              >
                {subtitle}
              </Heading>
            )}
          </Container>
        </Box>
      )}
    </Box>
    {credits ? <Credits caption={caption} {...credits} /> : null}
  </Box>
)

HeaderImage.propTypes = {
  image: PropTypes.any.isRequired,
  height: PropTypes.string,
  minHeight: PropTypes.string,
  maxHeight: PropTypes.string,
  title: PropTypes.string,
  subtitle: PropTypes.string,
  credits: PropTypes.shape({
    url: PropTypes.string.isRequired,
    author: PropTypes.string.isRequired,
  }),
  caption: PropTypes.string,
  background: PropTypes.string,
}

HeaderImage.defaultProps = {
  height: '60vh',
  minHeight: '20rem',
  maxHeight: null,
  title: null,
  subtitle: null,
  credits: null,
  caption: null,
  background: 'linear-gradient(transparent 0%, #00000066 30%)',
}

export default HeaderImage
