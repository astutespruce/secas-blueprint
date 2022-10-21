import React from 'react'
import PropTypes from 'prop-types'
import { withPrefix } from 'gatsby'

import { siteMetadata, pathPrefix } from '../../../gatsby-config'

const { title: baseTitle, description, author } = siteMetadata

// preload fonts so there is no flash of unstyled fonts
const fonts = [
  'source-sans-pro-400.woff2',
  'source-sans-pro-700.woff2',
  'source-sans-pro-900.woff2',
]

const SEO = ({ title: rawTitle }) => {
  const title = rawTitle ? `${rawTitle} | ${baseTitle}` : baseTitle

  const prefix = pathPrefix ? `/${pathPrefix}` : ''

  return (
    <>
      <title>{title}</title>
      <meta
        name="viewport"
        content="width=device-width, initial-scale=1, shrink-to-fit=no"
      />
      <meta name="lang" content="en" />
      <meta name="description" content={description} />
      <meta name="og:title" content={title} />
      <meta name="og:description" content={description} />
      <meta name="og:type" content="website" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:card" content="summary" />
      <meta name="twitter:creator" content={author} />
      <link rel="icon" type="image/png" href={`${prefix}/favicon.ico`} />
      <link
        rel="icon"
        type="image/svg+xml"
        href={`${prefix}/favicon-64x64.svg`}
      />
      <link
        rel="icon"
        type="image/png"
        sizes="16x16"
        href={`${prefix}/favicon-16x16.png`}
      />
      <link
        rel="icon"
        type="image/png"
        sizes="32x32"
        href={`${prefix}/favicon-32x32.png`}
      />
      <link
        rel="icon"
        type="image/png"
        sizes="64x64"
        href={`${prefix}/favicon-64x64.png`}
      />

      {/* Have to set HTML height manually for mobile browsers */}
      <style>{`html {height: 100%; width: 100%; margin: 0;}`}</style>

      {/* preload fonts so there is no flash of unstyled fonts */}
      {fonts.map((font) => {
        const url = withPrefix(`/fonts/${font}`)
        return (
          <link
            key={font}
            as="font"
            href={url}
            rel="preload"
            crossOrigin="anonymous"
          />
        )
      })}
    </>
  )
}

SEO.propTypes = {
  title: PropTypes.string,
}

SEO.defaultProps = {
  title: null,
}

export default SEO
