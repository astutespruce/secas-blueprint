import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Container, Heading } from 'theme-ui'
import { convertToBgImage } from 'gbimage-bridge'
import BackgroundImage from 'gatsby-background-image'

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
}) => (
  <>
    <BackgroundImage
      {...convertToBgImage(image)}
      style={{
        height,
        minHeight,
        maxHeight: maxHeight || height,
      }}
      alt=""
      preserveStackingContext
    >
      <Flex
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
          flexDirection: 'column',
          justifyContent: 'flex-end',
          alignItems: 'center',
        }}
      >
        {title && (
          <Box
            sx={{
              width: '100%',
              background: 'linear-gradient(transparent 0%, #0000009c 30%)',
              py: ['2rem', '3rem'],
            }}
          >
            <Container
              sx={{
                p: '1rem',
                textShadow: '1px 1px 3px #000',
                color: '#FFF',
                lineHeight: 1.1,
              }}
            >
              <Heading
                as="h1"
                sx={{
                  m: 0,
                  fontSize: '3rem',
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
                    fontSize: '1.5rem',
                  }}
                >
                  {subtitle}
                </Heading>
              )}
            </Container>
          </Box>
        )}
      </Flex>
    </BackgroundImage>
    {credits ? <Credits caption={caption} {...credits} /> : null}
  </>
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
}

HeaderImage.defaultProps = {
  height: '60vh',
  minHeight: '20rem',
  maxHeight: null,
  title: null,
  subtitle: null,
  credits: null,
  caption: null,
}

export default HeaderImage
