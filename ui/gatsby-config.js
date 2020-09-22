require('dotenv').config({
  path: `.env.${process.env.NODE_ENV}`,
})

module.exports = {
  siteMetadata: {
    siteUrl: process.env.SITE_URL || `https://blueprint.southatlanticlcc.org`,
    title: `South Atlantic Conservation Blueprint 2020`,
    description: `Provides custom reports for user-defined areas of interest`,
    author: `South Atlantic Conservation Blueprint`,
    contactEmail: `hilary_morris@fws.gov`,
    contactPhone: `19197070252`,
    apiToken: process.env.GATSBY_API_TOKEN,
    apiHost: process.env.GATSBY_API_HOST,
    tileHost: process.env.GATSBY_TILE_HOST,
    sentryDSN: process.env.GATSBY_SENTRY_DSN,
    googleAnalyticsId: process.env.GATSBY_GOOGLE_ANALYTICS_ID,
    mapboxToken: process.env.GATSBY_MAPBOX_API_TOKEN,
  },
  plugins: [
    {
      resolve: `@sentry/gatsby`,
      options: {
        dsn: process.env.GATSBY_SENTRY_DSN,
        beforeSend: (event, { originalException: error }) => {
          if (error && error.message) {
            // this error happens when ResizeObserver not able to deliver all observations within a single animation frame
            if (error.message.match(/ResizeObserver loop limit exceeded/i)) {
              return null
            }
          }
          return event
        },
      },
    },
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
    `gatsby-plugin-react-helmet`,
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
        typeName: ({ node }) => `${node.name}Json`,
      },
    },
    `gatsby-plugin-theme-ui`,
    `gatsby-transformer-sharp`,
    `gatsby-plugin-sharp`,
    {
      resolve: `gatsby-plugin-manifest`,
      options: {
        name: `South Atlantic Conservation Blueprint 2020`,
        short_name: `Blueprint 2020`,
        icon: 'src/images/logo.svg',
        start_url: `/`,
        background_color: `#0892d0`,
        theme_color: `#0892d0`,
        display: `minimal-ui`,
      },
    },
    {
      resolve: 'gatsby-plugin-robots-txt',
      options: {
        policy: [{ userAgent: '*', disallow: ['/services', '/api'] }],
      },
    },
  ],
}
