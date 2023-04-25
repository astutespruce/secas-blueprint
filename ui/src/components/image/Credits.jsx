import React from 'react'
import PropTypes from 'prop-types'
import { Box, NavLink } from 'theme-ui'

import { OutboundLink } from 'components/link'

const Credits = ({ author, url, caption }) => (
  <Box
    sx={{
      fontSize: 'smaller',
      textAlign: 'right',
      color: 'grey.8',
      pb: '0.25rem',
      px: '0.5rem',
      a: {
        color: 'grey.8',
        textDecoration: 'none',
      },
    }}
  >
    {caption ? `${caption} | ` : null}
    Photo:&nbsp;
    {url ? (
      // deliberately set high tab index on this, it is not important
      /* eslint-disable-next-line jsx-a11y/tabindex-no-positive */
      <OutboundLink to={url} tabIndex={100}>
        {author}
      </OutboundLink>
    ) : (
      author
    )}
  </Box>
)

Credits.propTypes = {
  author: PropTypes.string.isRequired,
  url: PropTypes.string,
  caption: PropTypes.string,
}

Credits.defaultProps = {
  url: NavLink,
  caption: null,
}

export default Credits
