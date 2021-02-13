require('dotenv').config({
  path: `.env.${process.env.NODE_ENV}`,
})

module.exports = {
  siteMetadata: {
    siteUrl: process.env.SITE_URL || `https://localhost`,
    title: `Southeast Conservation Blueprint`,
    description: `Provides user interface to explore the Southeast Conservation Blueprint and custom reports for user-defined areas of interest`,
    author: `Southeast Conservation Adaptation Strategy`,
    contactEmail: `hilary_morris@fws.gov`,
    contactPhone: `9197070252`,
    apiToken: process.env.GATSBY_API_TOKEN,
    apiHost: process.env.GATSBY_API_HOST,
    tileHost: process.env.GATSBY_TILE_HOST,
    sentryDSN: process.env.GATSBY_SENTRY_DSN,
    googleAnalyticsId: process.env.GATSBY_GOOGLE_ANALYTICS_ID,
    mapboxToken: process.env.GATSBY_MAPBOX_API_TOKEN,
    msFormURL: process.env.GATSBY_MS_FORM_URL,
    msFormEmail: process.env.GATSBY_MS_FORM_EMAIL,
    msFormName: process.env.GATSBY_MS_FORM_NAME,
    msFormOrg: process.env.GATSBY_MS_FORM_ORG,
    msFormUse: process.env.GATSBY_MS_FORM_USE,
    msFormAreaName: process.env.GATSBY_MS_FORM_AREANAME,
    msFormFileName: process.env.GATSBY_MS_FORM_FILENAME,
  },
  flags: {
    // FAST_DEV: true,
    FAST_REFRESH: true,
  },
  pathPrefix: process.env.SITE_ROOT_PATH || `/`,
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
    // {
    //   resolve: `gatsby-plugin-manifest`,
    //   options: {
    //     name: `Southeast Conservation Blueprint`,
    //     short_name: `Southeast Conservation Blueprint`,
    //     // icon: 'src/images/logo.svg',
    //     start_url: `/`,
    //     background_color: `#0892d0`,
    //     theme_color: `#0892d0`,
    //     display: `minimal-ui`,
    //   },
    // },
    {
      resolve: 'gatsby-plugin-robots-txt',
      options: {
        policy: [{ userAgent: '*', disallow: ['/services', '/api'] }],
      },
    },
  ],
}
