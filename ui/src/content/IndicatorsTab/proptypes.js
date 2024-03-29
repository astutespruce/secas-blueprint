import PropTypes from 'prop-types'

export const IndicatorPropType = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  ecosystem: PropTypes.shape({
    id: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    color: PropTypes.string.isRequired,
    borderColor: PropTypes.string.isRequired,
  }).isRequired,
  description: PropTypes.string.isRequired,
  goodThreshold: PropTypes.number,
  pixelValue: PropTypes.number,
  total: PropTypes.number,
  values: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
      percent: PropTypes.number.isRequired,
    })
  ).isRequired,
  valueLabel: PropTypes.string,
}

export const EcosystemPropType = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
  borderColor: PropTypes.string.isRequired,
  indicators: PropTypes.arrayOf(PropTypes.shape(IndicatorPropType)).isRequired,
}
