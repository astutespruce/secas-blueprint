import React from 'react'
import PropTypes from 'prop-types'
import { Button, Flex, Text } from 'theme-ui'
import { TimesCircle } from '@emotion-icons/fa-regular'

const MobileHeader = ({ type, name, location, onClose }) => (
  <Flex
    sx={{
      justifyContent: 'space-between',
      flex: '1 1 auto',
      alignItems: 'center',
      p: type === 'pixel' ? 0 : '0.25rem',
      lineHeight: 1.2,
      minHeight: '2.5rem',
    }}
  >
    {type === 'pixel' ? (
      <Text
        sx={{ pr: '0.5rem', flex: '1 1 auto', fontSize: 1, lineHeight: 1.4 }}
      >
        Coordinates:
        <br />
        {location.latitude.toPrecision(5)}°N,{' '}
        {location.longitude.toPrecision(5)}°
      </Text>
    ) : (
      <Text sx={{ pr: '0.5rem', flex: '1 1 auto', fontSize: 2 }}>{name}</Text>
    )}
    <Button
      variant="mobileHeaderClose"
      onClick={onClose}
      sx={{ flex: '0 0 auto', margin: 0, padding: 0 }}
    >
      <TimesCircle size="1.5em" />
    </Button>
  </Flex>
)

MobileHeader.propTypes = {
  type: PropTypes.string.isRequired,
  name: PropTypes.string,
  location: PropTypes.shape({
    latitude: PropTypes.number.isRequired,
    longitude: PropTypes.number.isRequired,
  }),
  onClose: PropTypes.func.isRequired,
}

MobileHeader.defaultProps = {
  name: null,
  location: null,
}

export default MobileHeader
