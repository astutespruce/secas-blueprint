/** @jsx jsx */

// eslint-disable-next-line no-unused-vars
import React from 'react'
import PropTypes from 'prop-types'
import { jsx } from 'theme-ui'

import {
  InfoCircle,
  Map,
  SearchLocation,
  QuestionCircle,
  Envelope,
  ExclamationCircle,
  ChartPie,
  SlidersH,
  UserFriends,
} from '@emotion-icons/fa-solid'

const Icon = ({ name, ...props }) => {
  switch (name) {
    case 'info': {
      return <InfoCircle {...props} />
    }
    case 'map':
    case 'unit-map': {
      return <Map {...props} />
    }
    case 'find': {
      return <SearchLocation {...props} />
    }
    case 'contact': {
      return <Envelope {...props} />
    }
    case 'selected-priorities': {
      return <ChartPie {...props} />
    }
    case 'selected-indicators': {
      return <SlidersH {...props} />
    }
    case 'selected-threats': {
      return <ExclamationCircle {...props} />
    }
    case 'selected-partners': {
      return <UserFriends {...props} />
    }
    default: {
      // fallthrough to make sure we always get an icon
      return <QuestionCircle {...props} />
    }
  }
}

Icon.propTypes = {
  name: PropTypes.string.isRequired,
}

export default Icon
