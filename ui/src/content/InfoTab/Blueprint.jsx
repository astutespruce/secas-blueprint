import React from 'react'

import { Box, Flex, Heading, Text } from 'theme-ui'

import { useBlueprintPriorities } from 'components/data'

const Blueprint = () => {
  const { priorities } = useBlueprintPriorities()

  return (
    <Box as="section" sx={{ mt: '2rem' }}>
      <Heading as="h3" sx={{ mb: '1rem' }}>
        Blueprint Priorities
        <Text sx={{ color: 'grey.8', fontSize: 0, fontWeight: 'normal' }}>
          (% of the Southeast Region)
        </Text>
      </Heading>

      {priorities.map(({ color, label, labelColor, description, percent }) => (
        <Box key={label}>
          <Box
            sx={{
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
            }}
          >
            <Flex
              sx={{ alignItems: 'center', width: ['100%', '100%', 'auto'] }}
            >
              <Flex
                sx={{
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '2.5rem',
                  height: '2.5rem',
                  borderRadius: '2rem',
                  bg: color,
                  mr: '0.5rem',
                  flex: '0 0 auto',
                }}
              >
                <Text
                  sx={{
                    color: labelColor || '#FFF',
                    fontSize: 0,
                    fontWeight: 'bold',
                  }}
                >
                  {percent}%
                </Text>
              </Flex>
              <Text as="div" sx={{ fontWeight: 'bold' }}>
                {label}
              </Text>
            </Flex>
          </Box>

          <Text
            as="p"
            sx={{ fontSize: [2, 1, 2], mb: '2rem', ml: '3rem', mt: '-0.5rem' }}
          >
            {description}
          </Text>
        </Box>
      ))}
    </Box>
  )
}

export default Blueprint
