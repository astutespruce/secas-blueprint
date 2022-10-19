import React from 'react'
import { Flex, Heading, Text } from 'theme-ui'

import { Link } from 'components/link'
import { useMapData } from 'components/data'
import HeaderButtons from './HeaderButtons'
import { useBreakpoints } from './Breakpoints'
import MobileHeader from './mobile/MobileHeader'

const Header = () => {
  const breakpoint = useBreakpoints()
  const isMobile = breakpoint === 0
  const { data, unsetData } = useMapData() || {} // will be null for non-map pages

  return (
    <Flex
      as="header"
      sx={{
        minHeight: '2.5rem',
        flex: '0 0 auto',
        justifyContent: 'space-between',
        alignItems: 'center',
        py: '0.3rem',
        pl: '0.5rem',
        pr: '1rem',
        bg: 'primary',
        color: '#FFF',
        zIndex: 1,
        boxShadow: '0 2px 6px #000',
      }}
    >
      {isMobile && data !== null ? (
        <MobileHeader {...data} onClose={unsetData} />
      ) : (
        <>
          <Flex
            sx={{
              alignItems: 'center',
            }}
          >
            <Link
              to="/"
              sx={{
                textDecoration: 'none !important',
                display: 'block',
                color: '#FFF',
              }}
            >
              <Flex
                sx={{
                  flexWrap: 'wrap',
                  alignItems: ['flex-start', 'flex-start', 'baseline'],
                  flexDirection: ['column', 'column', 'row'],
                }}
              >
                <Heading
                  as="h1"
                  sx={{
                    fontWeight: 700,
                    fontSize: ['10px', 1, 4],
                    lineHeight: 1,
                    m: 0,
                    breakInside: 'avoid',
                    flex: '0 1 auto',
                  }}
                >
                  Southeast
                </Heading>
                <Heading
                  as="h1"
                  sx={{
                    m: 0,
                    my: 0,
                    mx: [0, 0, '0.5rem'],
                    lineHeight: 1,
                    fontWeight: 700,
                    fontSize: [2, 3, 4],
                    breakInside: 'avoid',
                    flexGrow: 0,
                    flexShrink: 0,
                    flexBasis: ['100%', 'unset'],
                  }}
                >
                  Conservation Blueprint Explorer
                </Heading>
              </Flex>
            </Link>
          </Flex>
          {!isMobile && breakpoint >= 1 ? <HeaderButtons /> : null}
        </>
      )}
    </Flex>
  )
}

export default Header
