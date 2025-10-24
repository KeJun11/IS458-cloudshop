import {
  Box,
  Image,
  Text,
  HStack,
  VStack,
  IconButton,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  useColorModeValue,
  useToast,
} from '@chakra-ui/react'
import { FiTrash2 } from 'react-icons/fi'
import { type CartItem as CartItemType, type Product } from '../services/api'
import { useApp } from '../contexts/AppContext'

interface CartItemProps {
  item: CartItemType
  product: Product
}

export function CartItem({ item, product }: CartItemProps) {
  const { actions } = useApp()
  const toast = useToast()
  const bg = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  const handleQuantityChange = async (valueString: string) => {
    const value = parseInt(valueString) || 0
    if (value === 0) {
      await handleRemove()
      return
    }
    
    try {
      await actions.updateCartItem(item.productId, value)
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update quantity',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  const handleRemove = async () => {
    try {
      await actions.removeFromCart(item.productId)
      toast({
        title: 'Removed from cart',
        description: `${product.name} has been removed from your cart`,
        status: 'info',
        duration: 2000,
        isClosable: true,
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to remove item',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  const itemTotal = product.price * item.quantity

  return (
    <Box
      bg={bg}
      borderWidth="1px"
      borderColor={borderColor}
      borderRadius="lg"
      p={4}
    >
      <HStack spacing={4} align="start">
        <Image
          src={product.imageUrl}
          alt={product.name}
          boxSize="80px"
          objectFit="cover"
          borderRadius="md"
          fallbackSrc="https://via.placeholder.com/80x80?text=Product"
        />
        
        <VStack flex={1} align="stretch" spacing={2}>
          <HStack justify="space-between" align="start">
            <VStack align="start" spacing={1}>
              <Text fontWeight="semibold" fontSize="md">
                {product.name}
              </Text>
              <Text fontSize="sm" color="gray.600">
                {product.category}
              </Text>
              <Text fontSize="lg" fontWeight="bold" color="brand.500">
                ${product.price.toFixed(2)} each
              </Text>
            </VStack>
            
            <IconButton
              size="sm"
              variant="ghost"
              colorScheme="red"
              aria-label="Remove item"
              icon={<FiTrash2 />}
              onClick={handleRemove}
            />
          </HStack>
          
          <HStack justify="space-between" align="center">
            <HStack spacing={2} align="center">
              <Text fontSize="sm">Quantity:</Text>
              <NumberInput
                size="sm"
                maxW={20}
                value={item.quantity}
                min={1}
                max={product.stock}
                onChange={handleQuantityChange}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </HStack>
            
            <VStack align="end" spacing={1}>
              <Text fontSize="sm" color="gray.600">
                Subtotal:
              </Text>
              <Text fontSize="lg" fontWeight="bold">
                ${itemTotal.toFixed(2)}
              </Text>
            </VStack>
          </HStack>
        </VStack>
      </HStack>
    </Box>
  )
}
