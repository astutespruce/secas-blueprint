import React from 'react'
import PropTypes from 'prop-types'
import Helmet from 'react-helmet'
import { useStaticQuery, graphql } from 'gatsby'

function SEO({ description, meta, title }) {
  const { site } = useStaticQuery(
    graphql`
      query {
        site {
          siteMetadata {
            title
            description
            author
          }
        }
      }
    `
  )

  const metaDescription = description || site.siteMetadata.description

  return (
    <Helmet
      htmlAttributes={{
        lang: 'en',
        viewport: 'width=device-width, initial-scale=1, shrink-to-fit=no',
      }}
      title={title}
      titleTemplate={title ? `%s | ${site.siteMetadata.title}` : `%s`}
      meta={[
        {
          name: `description`,
          content: metaDescription,
        },
        {
          property: `og:title`,
          content: title,
        },
        {
          property: `og:description`,
          content: metaDescription,
        },
        {
          property: `og:type`,
          content: `website`,
        },
        {
          name: `twitter:card`,
          content: `summary`,
        },
        {
          name: `twitter:creator`,
          content: site.siteMetadata.author,
        },
        {
          name: `twitter:title`,
          content: title,
        },
        {
          name: `twitter:description`,
          content: metaDescription,
        },
      ].concat(meta)}
      // link={[
      //   { rel: 'icon', type: 'image/png', href: '/favicon.ico' },
      //   { rel: 'icon', type: 'image/svg+xml', href: '/favicon-64x64.svg' },
      //   {
      //     rel: 'icon',
      //     sizes: '16x16',
      //     type: 'image/png',
      //     href: '/favicon-16x16.png',
      //   },
      //   {
      //     rel: 'icon',
      //     sizes: '32x32',
      //     type: 'image/png',
      //     href: '/favicon-32x32.png',
      //   },
      //   {
      //     rel: 'icon',
      //     sizes: '64x64',
      //     type: 'image/png',
      //     href: '/favicon-64x64.png',
      //   },
      // ]}
    >
      {/* Have to set HTML height manually for mobile browsers */}
      <style>{`html {height: 100%; width: 100%; margin: 0;}`}</style>
    </Helmet>
  )
}

SEO.propTypes = {
  description: PropTypes.string,
  meta: PropTypes.arrayOf(PropTypes.object),
  title: PropTypes.string,
}

SEO.defaultProps = {
  meta: [],
  title: null,
  description: null,
}

export default SEO
