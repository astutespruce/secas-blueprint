import React from 'react'

import { Box, Flex, Heading, Text } from 'theme-ui'

import { useBlueprintCategories } from 'components/data'

const Blueprint = () => {
  const { categories } = useBlueprintCategories()

  return (
    <Box as="section" sx={{ mt: '2rem' }}>
      <Heading as="h3" sx={{ mb: '1rem' }}>
        Blueprint Categories
        <Text sx={{ color: 'grey.8', fontSize: 0, fontWeight: 'normal' }}>
          (% of the Southeast Region)
        </Text>
      </Heading>

      {categories.map(({ color, label, description, percent }) => (
        <Flex
          key={label}
          sx={{
            alignItems: 'flex-start',
            '&:not(:first-of-type)': {
              mt: '2rem',
            },
          }}
        >
          <Flex
            sx={{
              alignItems: 'center',
              justifyContent: 'center',
              width: '3rem',
              height: '3rem',
              borderRadius: '3rem',
              bg: color,
              mr: '1rem',
              flex: '0 0 auto',
            }}
          >
            <Text
              sx={{
                color: '#FFF',
                fontSize: 1,
                fontWeight: 'bold',
              }}
            >
              {percent}%
            </Text>
          </Flex>

          <Box>
            <Text as="div" sx={{ fontWeight: 'bold', fontSize: 3 }}>
              {label}
            </Text>

            <Text as="p">{description}</Text>
          </Box>
        </Flex>
      ))}
    </Box>
  )
}

export default Blueprint
