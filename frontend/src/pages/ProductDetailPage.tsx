import {
  Container,
  VStack,
  HStack,
  Text,
  Box,
  Heading,
  Button,
  Image,
  Badge,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  SimpleGrid,
  Divider,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
} from '@chakra-ui/react'
import { FiShoppingCart, FiArrowLeft } from 'react-icons/fi'
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ProductCard } from '../components/ProductCard'
import { useApp } from '../contexts/AppContext'
import { type Product } from '../services/api'

export function ProductDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { state, actions } = useApp()
  const navigate = useNavigate()
  const toast = useToast()
  const [quantity, setQuantity] = useState(1)
  const [isAddingToCart, setIsAddingToCart] = useState(false)

  const product = state.products.find(p => p.id === id)
  const relatedProducts = state.products
    .filter(p => p.id !== id && p.category === product?.category)
    .slice(0, 4)

  useEffect(() => {
    if (product) {
      // Track product view for recommendations
      actions.trackProductView(product)
    }
  }, [product, actions])

  const handleAddToCart = async () => {
    if (!product) return

    setIsAddingToCart(true)
    try {
      await actions.addToCart(product, quantity)
      toast({
        title: 'Added to cart',
        description: `${quantity} × ${product.name} added to your cart`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to add item to cart',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setIsAddingToCart(false)
    }
  }

  const handleProductClick = (clickedProduct: Product) => {
    navigate(`/product/${clickedProduct.id}`)
  }

  if (state.loading) {
    return (
      <Container maxW="7xl" py={8}>
        <VStack spacing={8} align="center">
          <Spinner size="xl" color="brand.500" />
          <Text>Loading product...</Text>
        </VStack>
      </Container>
    )
  }

  if (!product) {
    return (
      <Container maxW="7xl" py={8}>
        <Alert status="error">
          <AlertIcon />
          Product not found
        </Alert>
        <Button
          mt={4}
          leftIcon={<FiArrowLeft />}
          onClick={() => navigate('/products')}
        >
          Back to Products
        </Button>
      </Container>
    )
  }

  return (
    <Container maxW="7xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Back Button */}
        <Button
          leftIcon={<FiArrowLeft />}
          variant="ghost"
          alignSelf="flex-start"
          onClick={() => navigate(-1)}
        >
          Back
        </Button>

        {/* Product Details */}
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
          {/* Product Image */}
          <Box>
            <Image
              src={product.imageUrl}
              alt={product.name}
              w="full"
              h={{ base: "300px", md: "500px" }}
              objectFit="cover"
              borderRadius="lg"
              fallbackSrc="https://via.placeholder.com/500x500?text=Product+Image"
            />
          </Box>

          {/* Product Info */}
          <VStack align="stretch" spacing={6}>
            <VStack align="stretch" spacing={3}>
              <HStack justify="space-between" align="start">
                <Heading size="xl">{product.name}</Heading>
                <Badge colorScheme="blue" fontSize="md" px={3} py={1}>
                  {product.category}
                </Badge>
              </HStack>
              
              <Text fontSize="3xl" fontWeight="bold" color="brand.500">
                ${product.price.toFixed(2)}
              </Text>
              
              <Text fontSize="lg" color="gray.600" lineHeight="tall">
                {product.description}
              </Text>
            </VStack>

            <Divider />

            {/* Stock Status */}
            <HStack>
              <Text fontWeight="medium">Stock:</Text>
              <Text color={product.stock > 10 ? "green.500" : product.stock > 0 ? "orange.500" : "red.500"}>
                {product.stock > 0 ? `${product.stock} available` : 'Out of stock'}
              </Text>
            </HStack>

            {/* Quantity and Add to Cart */}
            {product.stock > 0 && (
              <VStack align="stretch" spacing={4}>
                <HStack>
                  <Text fontWeight="medium">Quantity:</Text>
                  <NumberInput
                    value={quantity}
                    onChange={(valueString) => setQuantity(parseInt(valueString) || 1)}
                    min={1}
                    max={product.stock}
                    maxW="100px"
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </HStack>

                <HStack spacing={4}>
                  <Button
                    size="lg"
                    colorScheme="brand"
                    leftIcon={<FiShoppingCart />}
                    onClick={handleAddToCart}
                    isLoading={isAddingToCart}
                    loadingText="Adding..."
                    flex={1}
                  >
                    Add to Cart
                  </Button>
                  
                  <Button
                    size="lg"
                    variant="outline"
                    onClick={() => navigate('/cart')}
                  >
                    View Cart
                  </Button>
                </HStack>
              </VStack>
            )}

            {product.stock === 0 && (
              <Alert status="warning">
                <AlertIcon />
                This product is currently out of stock
              </Alert>
            )}
          </VStack>
        </SimpleGrid>

        {/* Related Products */}
        {relatedProducts.length > 0 && (
          <Box>
            <Heading size="lg" mb={6}>
              Related Products
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
              {relatedProducts.map((relatedProduct) => (
                <ProductCard
                  key={relatedProduct.id}
                  product={relatedProduct}
                  onProductClick={handleProductClick}
                />
              ))}
            </SimpleGrid>
          </Box>
        )}
      </VStack>
    </Container>
  )
}
