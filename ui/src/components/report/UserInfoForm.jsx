import React from 'react'
import { useFormContext } from 'react-hook-form'
import { Text, Box, Grid, Heading, Input, Textarea } from 'theme-ui'

const inputCSS = {
  width: '100%',
}

const invalidInputCSS = {
  ...inputCSS,
  borderLeftWidth: '0.5rem !important',
  borderColor: 'error',
  '&:focus': {
    borderColor: 'error',
  },
}

const UserInfoForm = () => {
  const { errors, register } = useFormContext()

  return (
    <Box
      sx={{
        mt: '4rem',
        '& label': {
          display: 'block',
        },
      }}
    >
      <Heading
        as="h3"
        sx={{
          mb: '1rem',
        }}
      >
        Please tell us about yourself (optional)
      </Heading>

      <Text sx={{ fontSize: 1, color: 'grey.7', mb: '1rem' }}>
        We use this information to provide statistics about how the Blueprint is
        being used and better understand how the Blueprint is being used so that
        we can prioritize improvements.
      </Text>

      <Grid columns="1fr 2fr" gap="2rem">
        <Box>
          <Box>
            <Text as="label" htmlFor="userEmail">
              Email address:
              {errors.userEmail ? (
                <Text
                  as="span"
                  sx={{
                    color: 'error',
                    fontStyle: 'italic',
                    fontSize: 0,
                    ml: '0.5em',
                  }}
                >
                  please use a valid email
                </Text>
              ) : null}
            </Text>
            <Input
              name="userEmail"
              ref={register({
                required: false,
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                },
              })}
              sx={errors.userEmail ? invalidInputCSS : inputCSS}
            />
          </Box>

          <Box sx={{ mt: '1rem' }}>
            <Text as="label" htmlFor="userName">
              Name:
            </Text>
            <Input
              name="userName"
              ref={register({ required: false })}
              sx={errors.userName ? invalidInputCSS : inputCSS}
            />
          </Box>

          <Box sx={{ mt: '1rem' }}>
            <Text as="label" htmlFor="userOrg">
              Organization:
            </Text>
            <Input
              name="userOrg"
              ref={register({ required: false })}
              sx={errors.userOrg ? invalidInputCSS : inputCSS}
            />
          </Box>
        </Box>

        <Box>
          <Text as="label" htmlFor="userUse">
            How will you use this report?
          </Text>
          <Textarea
            name="userUse"
            rows={9}
            ref={register({ required: false })}
            sx={errors.userUse ? invalidInputCSS : inputCSS}
          />
        </Box>
      </Grid>
    </Box>
  )
}

export default UserInfoForm
