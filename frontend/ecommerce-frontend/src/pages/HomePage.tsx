import {
  Container,
  VStack,
  Text,
  SimpleGrid,
  Box,
  Heading,
  Button,
  HStack,
  Spinner,
  Alert,
  AlertIcon,
} from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'
import { ProductCard } from '../components/ProductCard'
import { useApp } from '../contexts/AppContext'
import { type Product } from '../services/api'

export function HomePage() {
  const { state } = useApp()
  const navigate = useNavigate()

  const handleProductClick = (product: Product) => {
    navigate(`/product/${product.id}`)
  }

  if (state.loading) {
    return (
      <Container maxW="7xl" py={8}>
        <VStack spacing={8} align="center">
          <Spinner size="xl" color="brand.500" />
          <Text>Loading products...</Text>
        </VStack>
      </Container>
    )
  }

  if (state.error) {
    return (
      <Container maxW="7xl" py={8}>
        <Alert status="error">
          <AlertIcon />
          {state.error}
        </Alert>
      </Container>
    )
  }

  const featuredProducts = state.products.slice(0, 6)
  const hasRecommendations = state.recommendations.length > 0

  return (
    <Container maxW="7xl" py={8}>
      <VStack spacing={12} align="stretch">
        {/* Hero Section */}
        <Box textAlign="center" py={8}>
          <Heading size="2xl" mb={4}>
            Welcome to CloudShop
          </Heading>
          <Text fontSize="xl" color="gray.600" mb={6}>
            Discover amazing products with our cloud-powered e-commerce platform
          </Text>
          <HStack spacing={4} justify="center">
            <Button size="lg" colorScheme="brand" onClick={() => navigate('/products')}>
              Shop Now
            </Button>
            <Button size="lg" variant="outline" onClick={() => navigate('/cart')}>
              View Cart ({state.cart.items.length})
            </Button>
          </HStack>
        </Box>

        {/* Recommendations Section */}
        {hasRecommendations && (
          <Box>
            <Heading size="lg" mb={6}>
              Recommended for You
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
              {state.recommendations.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onProductClick={handleProductClick}
                />
              ))}
            </SimpleGrid>
          </Box>
        )}

        {/* Featured Products Section */}
        <Box>
          <HStack justify="space-between" align="center" mb={6}>
            <Heading size="lg">Featured Products</Heading>
            <Button variant="outline" onClick={() => navigate('/products')}>
              View All Products
            </Button>
          </HStack>
          
          {featuredProducts.length > 0 ? (
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
              {featuredProducts.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onProductClick={handleProductClick}
                />
              ))}
            </SimpleGrid>
          ) : (
            <Box textAlign="center" py={8}>
              <Text fontSize="lg" color="gray.600">
                No products available at the moment.
              </Text>
            </Box>
          )}
        </Box>

        {/* Categories Section */}
        <Box>
          <Heading size="lg" mb={6}>
            Shop by Category
          </Heading>
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
            {['Electronics', 'Accessories', 'Home & Garden', 'Sports'].map((category) => (
              <Button
                key={category}
                variant="outline"
                size="lg"
                h="60px"
                onClick={() => navigate(`/products?category=${category}`)}
              >
                {category}
              </Button>
            ))}
          </SimpleGrid>
        </Box>
      </VStack>
    </Container>
  )
}
