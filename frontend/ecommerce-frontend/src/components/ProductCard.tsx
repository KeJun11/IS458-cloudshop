import {
  Box,
  Image,
  Text,
  Button,
  VStack,
  HStack,
  Badge,
  useColorModeValue,
  useToast,
} from '@chakra-ui/react'
import { FiShoppingCart } from 'react-icons/fi'
import { type Product } from '../services/api'
import { useApp } from '../contexts/AppContext'

interface ProductCardProps {
  product: Product
  onProductClick?: (product: Product) => void
}

export function ProductCard({ product, onProductClick }: ProductCardProps) {
  const { actions } = useApp()
  const toast = useToast()
  const bg = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  const handleAddToCart = async (e: React.MouseEvent) => {
    e.stopPropagation() // Prevent triggering the product click
    try {
      await actions.addToCart(product)
      toast({
        title: 'Added to cart',
        description: `${product.name} has been added to your cart`,
        status: 'success',
        duration: 2000,
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
    }
  }

  const handleProductClick = () => {
    if (onProductClick) {
      onProductClick(product)
    }
    // Track product view for recommendations
    actions.trackProductView(product)
  }

  return (
    <Box
      bg={bg}
      borderWidth="1px"
      borderColor={borderColor}
      borderRadius="lg"
      overflow="hidden"
      cursor="pointer"
      transition="all 0.2s"
      _hover={{
        transform: 'translateY(-2px)',
        shadow: 'lg',
      }}
      onClick={handleProductClick}
    >
      <Image
        src={product.imageUrl}
        alt={product.name}
        h="200px"
        w="full"
        objectFit="cover"
        fallbackSrc="https://via.placeholder.com/300x200?text=Product+Image"
      />
      
      <VStack p={4} align="stretch" spacing={3}>
        <VStack align="stretch" spacing={2}>
          <HStack justify="space-between" align="start">
            <Text fontSize="lg" fontWeight="semibold" noOfLines={2}>
              {product.name}
            </Text>
            <Badge colorScheme="blue" fontSize="xs">
              {product.category}
            </Badge>
          </HStack>
          
          <Text fontSize="sm" color="gray.600" noOfLines={2}>
            {product.description}
          </Text>
        </VStack>

        <HStack justify="space-between" align="center">
          <Text fontSize="xl" fontWeight="bold" color="brand.500">
            ${product.price.toFixed(2)}
          </Text>
          
          <Button
            size="sm"
            leftIcon={<FiShoppingCart />}
            colorScheme="brand"
            onClick={handleAddToCart}
            isDisabled={product.stock === 0}
          >
            {product.stock === 0 ? 'Out of Stock' : 'Add to Cart'}
          </Button>
        </HStack>

        {product.stock > 0 && product.stock <= 10 && (
          <Text fontSize="xs" color="orange.500" textAlign="center">
            Only {product.stock} left in stock!
          </Text>
        )}
      </VStack>
    </Box>
  )
}
