import styled from '@emotion/styled'

const ImageCredits = styled.div`
  font-size: small;
  text-align: right;
  margin-right: 1rem;
  color: ${({ theme }) => theme.colors.grey[6]};

  a {
    color: ${({ theme }) => theme.colors.grey[6]};
    text-decoration: underline;
  }
`

export default ImageCredits
