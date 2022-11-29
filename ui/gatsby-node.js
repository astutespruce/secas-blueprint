const path = require('path-browserify')
/**
 * Enable absolute imports with `/src` as root.
 * See: https://github.com/alampros/gatsby-plugin-resolve-src/issues/4
 */
exports.onCreateWebpackConfig = ({ actions, stage, loaders, plugins }) => {
  const config = {
    resolve: {
      alias: {
        assert: require.resolve('assert'),
        os: require.resolve('os-browserify/browser'),
        path: require.resolve('path-browserify'),
        stream: require.resolve('stream-browserify'),
        util: require.resolve('util'),
        zlib: require.resolve('browserify-zlib'),
      },
      fallback: {
        fs: false,
        crypto: false,
      },

      // Enable absolute imports with `/src` as root.
      modules: [path.resolve(__dirname, 'src'), 'node_modules'],
    },
    plugins: [
      plugins.provide({
        process: 'process/browser',
        Buffer: ['buffer', 'Buffer'],
      }),
    ],
    module: {
      rules: [
        {
          test: /\.(glsl|vs|fs|vert|frag)$/,
          exclude: /node_modules/,
          use: ['raw-loader'],
        },
      ],
    },
  }

  // when building HTML, window is not defined, so mapbox-gl causes the build to blow up
  if (stage === 'build-html') {
    config.module = {
      rules: [
        {
          test: /mapbox-gl/,
          use: loaders.null(),
        },
      ],
    }
  }

  actions.setWebpackConfig(config)
}
