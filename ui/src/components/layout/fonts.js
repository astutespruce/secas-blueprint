import { css } from '@emotion/react'
import { withPrefix } from 'gatsby'

export // font declaration extracted from typography-source-sans-pro index.css
// NOTE: no italic typefaces are currently used in this app

const prefix = withPrefix('/fonts')

const fonts = css`
  @font-face {
    font-family: 'Source Sans Pro';
    font-style: normal;
    font-display: swap;
    font-weight: 400;
    src: local('Source Sans Pro Regular normal'),
      local('Source Sans Pro-Regularnormal'),
      url('${prefix}/source-sans-pro-400.woff2') format('woff2'),
      url('${prefix}/source-sans-pro-400.woff') format('woff');
  }
  @font-face {
    font-family: 'Source Sans Pro';
    font-style: normal;
    font-display: swap;
    font-weight: 700;
    src: local('Source Sans Pro Bold normal'),
      local('Source Sans Pro-Boldnormal'),
      url('${prefix}/source-sans-pro-700.woff2') format('woff2'),
      url('${prefix}/source-sans-pro-700.woff') format('woff');
  }
  @font-face {
    font-family: 'Source Sans Pro';
    font-style: normal;
    font-display: swap;
    font-weight: 900;
    src: local('Source Sans Pro Black normal'),
      local('Source Sans Pro-Blacknormal'),
      url('${prefix}/source-sans-pro-900.woff2') format('woff2'),
      url('${prefix}/source-sans-pro-900.woff') format('woff');
  }
`
