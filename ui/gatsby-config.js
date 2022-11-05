require('dotenv').config({
  path: `.env.${process.env.NODE_ENV}`,
})

const theme = require('./src/theme')

const rootPath = process.env.SITE_ROOT_PATH || `/`

module.exports = {
  siteMetadata: {
    siteUrl: process.env.SITE_URL || `https://localhost`,
    title: `Southeast Conservation Blueprint Explorer`,
    description: `Provides user interface to explore the Southeast Conservation Blueprint and custom reports for user-defined areas of interest`,
    author: `Southeast Conservation Adaptation Strategy`,
    contactEmail: `hilary_morris@fws.gov`,
    contactPhone: `9197070252`,
    apiToken: process.env.GATSBY_API_TOKEN,
    apiHost: process.env.GATSBY_API_HOST,
    tileHost: process.env.GATSBY_TILE_HOST,
    sentryDSN: process.env.GATSBY_SENTRY_DSN,
    sentryENV: process.env.GATSBY_SENTRY_ENV || 'development',
    googleAnalyticsId: process.env.GATSBY_GOOGLE_ANALYTICS_ID,
    mapboxToken: process.env.GATSBY_MAPBOX_API_TOKEN,
  },
  flags: {
    FAST_DEV: true,
    DEV_SSR: false, // appears to throw '"filePath" is not allowed to be empty' when true
    PARALLEL_SOURCING: process.env.NODE_ENV !== `production`, // uses a lot of memory on server
  },
  pathPrefix: rootPath,
  plugins: [
    {
      resolve: `gatsby-plugin-google-gtag`,
      options: {
        trackingIds: [process.env.GATSBY_GOOGLE_ANALYTICS_ID],
        gtagConfig: {
          anonymize_ip: true,
        },
        pluginConfig: {
          head: true,
          respectDNT: true,
        },
      },
    },
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `images`,
        path: `${__dirname}/src/images`,
      },
    },
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `constants`,
        path: `${__dirname}/../constants`,
      },
    },
    {
      resolve: `gatsby-transformer-json`,
      options: {
        // name the top-level type after the filename
        typeName: ({ node: { name, relativeDirectory } }) => {
          // combine all indicators into a single JSON endpoint
          if (relativeDirectory === 'indicators') {
            return 'indicatorsJson'
          }

          return `${name}Json`
        },
      },
    },
    `gatsby-plugin-emotion`,
    {
      resolve: `gatsby-plugin-theme-ui`,
      options: {
        injectColorFlashScript: false,
        preset: theme,
      },
    },
    `gatsby-transformer-sharp`,
    `gatsby-plugin-sharp`,
    {
      resolve: `gatsby-plugin-manifest`,
      options: {
        name: `Southeast Conservation Blueprint Explorer`,
        short_name: `Southeast Blueprint Explorer`,
        icon: 'src/images/logo.svg',
        start_url: `/`,
        background_color: `#4279A6`,
        theme_color: `#4279A6`,
        display: `minimal-ui`,
      },
    },
    {
      resolve: 'gatsby-plugin-robots-txt',
      options: {
        host: process.env.SITE_URL || `https://localhost`,
        policy: [{ userAgent: '*', disallow: ['/services', '*/api/*'] }],
      },
    },
    `gatsby-plugin-sitemap`,
  ],
}
