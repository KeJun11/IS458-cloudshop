import {
  Container,
  VStack,
  HStack,
  Text,
  Box,
  Heading,
  Button,
  Divider,
  Alert,
  AlertIcon,
  useColorModeValue,
} from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'
import { CartItem } from '../components/CartItem'
import { useApp } from '../contexts/AppContext'

export function CartPage() {
  const { state, actions } = useApp()
  const navigate = useNavigate()
  const bg = useColorModeValue('gray.50', 'gray.900')

  const cartItems = state.cart.items.map(item => ({
    item,
    product: state.products.find(p => p.id === item.productId)!
  })).filter(({ product }) => product) // Filter out items where product is not found

  const handleClearCart = () => {
    actions.clearCart()
  }

  const handleCheckout = () => {
    navigate('/checkout')
  }

  if (cartItems.length === 0) {
    return (
      <Container maxW="4xl" py={8}>
        <VStack spacing={8} align="center" py={12}>
          <Heading size="lg">Your Cart is Empty</Heading>
          <Text fontSize="lg" color="gray.600" textAlign="center">
            Looks like you haven't added any items to your cart yet.
          </Text>
          <Button size="lg" colorScheme="brand" onClick={() => navigate('/products')}>
            Start Shopping
          </Button>
        </VStack>
      </Container>
    )
  }

  return (
    <Container maxW="4xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <Heading size="xl">Shopping Cart</Heading>
          <Button variant="outline" colorScheme="red" onClick={handleClearCart}>
            Clear Cart
          </Button>
        </HStack>

        {/* Cart Items */}
        <VStack spacing={4} align="stretch">
          {cartItems.map(({ item, product }) => (
            <CartItem key={item.productId} item={item} product={product} />
          ))}
        </VStack>

        {/* Cart Summary */}
        <Box bg={bg} p={6} borderRadius="lg" borderWidth="1px">
          <VStack spacing={4} align="stretch">
            <Heading size="md">Order Summary</Heading>
            
            <VStack spacing={2} align="stretch">
              <HStack justify="space-between">
                <Text>Items ({state.cart.items.reduce((total, item) => total + item.quantity, 0)}):</Text>
                <Text>${state.cart.total.toFixed(2)}</Text>
              </HStack>
              
              <HStack justify="space-between">
                <Text>Shipping:</Text>
                <Text>Free</Text>
              </HStack>
              
              <HStack justify="space-between">
                <Text>Tax:</Text>
                <Text>${(state.cart.total * 0.08).toFixed(2)}</Text>
              </HStack>
              
              <Divider />
              
              <HStack justify="space-between">
                <Text fontSize="lg" fontWeight="bold">Total:</Text>
                <Text fontSize="lg" fontWeight="bold" color="brand.500">
                  ${(state.cart.total * 1.08).toFixed(2)}
                </Text>
              </HStack>
            </VStack>

            <VStack spacing={3} pt={4}>
              <Button
                size="lg"
                colorScheme="brand"
                w="full"
                onClick={handleCheckout}
              >
                Proceed to Checkout
              </Button>
              
              <Button
                size="lg"
                variant="outline"
                w="full"
                onClick={() => navigate('/products')}
              >
                Continue Shopping
              </Button>
            </VStack>
          </VStack>
        </Box>

        {/* Additional Info */}
        <Alert status="info">
          <AlertIcon />
          <VStack align="start" spacing={1}>
            <Text fontWeight="medium">Free shipping on all orders!</Text>
            <Text fontSize="sm">
              Your order will be processed securely through our cloud infrastructure.
            </Text>
          </VStack>
        </Alert>
      </VStack>
    </Container>
  )
}
