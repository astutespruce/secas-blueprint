import React from 'react'
import PropTypes from 'prop-types'
import { Check } from '@emotion-icons/fa-solid'
import { Box, Flex, Text } from 'theme-ui'

// const SLRCategories = ({ categories, value: currentValue }) => (
//   <Box sx={{ ml: '0.5rem', mt: '0.5rem' }}>
//     {categories.map(({ value, label }) => (
//       <Flex
//         key={value}
//         sx={{
//           alignItems: 'baseline',
//           justifyContent: 'space-between',
//           pl: '0.5rem',
//           borderBottom: '1px solid',
//           borderBottomColor: 'grey.2',
//           pb: '0.25rem',
//           '&:not(:first-of-type)': {
//             mt: '0.25rem',
//           },
//         }}
//       >
//         <Text
//           sx={{
//             flex: '1 1 auto',
//             color: value === currentValue ? 'text' : 'grey.6',
//             fontWeight: value === currentValue ? 'bold' : 'normal',
//           }}
//         >
//           {label}
//         </Text>
//         {value === currentValue ? (
//           <Box sx={{ flex: '0 0 auto' }}>
//             <Check size="1em" />
//           </Box>
//         ) : null}
//       </Flex>
//     ))}
//   </Box>
// )

const SLRCategories = ({ categories, value: currentValue }) => (
  <Flex sx={{ mt: '0.5rem', alignItems: 'center' }}>
    {categories.map(({ value, label }, i) => (
      <Box
        sx={{
          flex: '1 1 auto',
          borderWidth: '1px solid',
          borderStyle: 'solid',
          borderColor: currentValue <= value ? '#004da8' : 'grey.2',
          borderLeftWidth: i > 0 && currentValue !== value ? 0 : '1px',
          bg: currentValue <= value ? '#004da8b3' : 'inherit',
        }}
      >
        <Text
          sx={{
            textAlign: 'center',
            fontWeight: currentValue <= value ? 'bold' : 'inherit',
            color: currentValue <= value ? '#FFFFFF' : 'grey.8',
          }}
        >
          {label}
        </Text>
      </Box>
    ))}
  </Flex>
)

SLRCategories.propTypes = {
  categories: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.number.isRequired,
      label: PropTypes.string.isRequired,
      description: PropTypes.string,
    })
  ).isRequired,
  value: PropTypes.number,
}

SLRCategories.defaultProps = {
  value: null,
}

export default SLRCategories
