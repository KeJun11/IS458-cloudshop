import {
  Box,
  Flex,
  Text,
  IconButton,
  Badge,
  HStack,
  useColorModeValue,
  Container,
  Button,
} from '@chakra-ui/react'
import { FiShoppingCart, FiUser } from 'react-icons/fi'
import { Link, useNavigate } from 'react-router-dom'
import { useApp } from '../contexts/AppContext'

export function Header() {
  const { state } = useApp()
  const navigate = useNavigate()
  const bg = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  const cartItemsCount = state.cart.items.reduce((total, item) => total + item.quantity, 0)

  return (
    <Box bg={bg} borderBottom="1px" borderColor={borderColor} position="sticky" top={0} zIndex={1000}>
      <Container maxW="7xl">
        <Flex h={16} alignItems="center" justifyContent="space-between">
          {/* Logo */}
          <Link to="/">
            <Text fontSize="xl" fontWeight="bold" color="brand.500">
              CloudShop
            </Text>
          </Link>

          {/* Navigation */}
          <HStack spacing={8} alignItems="center">
            <HStack as="nav" spacing={4} display={{ base: 'none', md: 'flex' }}>
              <Link to="/">
                <Button variant="ghost">Home</Button>
              </Link>
              <Link to="/products">
                <Button variant="ghost">Products</Button>
              </Link>
            </HStack>

            {/* User Actions */}
            <HStack spacing={2}>
              {/* User Profile */}
              <IconButton
                size="sm"
                variant="ghost"
                aria-label="User profile"
                icon={<FiUser />}
                onClick={() => navigate('/profile')}
              />

              {/* Shopping Cart */}
              <Box position="relative">
                <IconButton
                  size="sm"
                  variant="ghost"
                  aria-label="Shopping cart"
                  icon={<FiShoppingCart />}
                  onClick={() => navigate('/cart')}
                />
                {cartItemsCount > 0 && (
                  <Badge
                    colorScheme="red"
                    position="absolute"
                    top="-1"
                    right="-1"
                    fontSize="xs"
                    borderRadius="full"
                    minW="20px"
                    h="20px"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                  >
                    {cartItemsCount}
                  </Badge>
                )}
              </Box>
            </HStack>
          </HStack>
        </Flex>
      </Container>
    </Box>
  )
}
