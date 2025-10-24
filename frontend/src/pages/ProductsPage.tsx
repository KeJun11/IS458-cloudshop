import {
  Container,
  VStack,
  HStack,
  Text,
  SimpleGrid,
  Box,
  Heading,
  Select,
  Input,
  InputGroup,
  InputLeftElement,
  Spinner,
  Alert,
  AlertIcon,
} from '@chakra-ui/react'
import { FiSearch } from 'react-icons/fi'
import { useState, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { ProductCard } from '../components/ProductCard'
import { useApp } from '../contexts/AppContext'
import { type Product } from '../services/api'

export function ProductsPage() {
  const { state } = useApp()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState('name')
  const [filterCategory, setFilterCategory] = useState(searchParams.get('category') || '')

  const handleProductClick = (product: Product) => {
    navigate(`/product/${product.id}`)
  }

  // Get unique categories
  const categories = useMemo(() => {
    const uniqueCategories = [...new Set(state.products.map(p => p.category))]
    return uniqueCategories.sort()
  }, [state.products])

  // Filter and sort products
  const filteredAndSortedProducts = useMemo(() => {
    let filtered = state.products

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(term) ||
        product.description.toLowerCase().includes(term) ||
        product.category.toLowerCase().includes(term)
      )
    }

    // Filter by category
    if (filterCategory) {
      filtered = filtered.filter(product => product.category === filterCategory)
    }

    // Sort products
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name)
        case 'price-low':
          return a.price - b.price
        case 'price-high':
          return b.price - a.price
        case 'category':
          return a.category.localeCompare(b.category)
        default:
          return 0
      }
    })

    return sorted
  }, [state.products, searchTerm, filterCategory, sortBy])

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

  return (
    <Container maxW="7xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="xl" mb={2}>
            Products
          </Heading>
          <Text color="gray.600">
            Discover our amazing collection of products
          </Text>
        </Box>

        {/* Filters and Search */}
        <Box>
          <VStack spacing={4} align="stretch">
            {/* Search */}
            <InputGroup>
              <InputLeftElement pointerEvents="none">
                <FiSearch color="gray.300" />
              </InputLeftElement>
              <Input
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </InputGroup>

            {/* Filters */}
            <HStack spacing={4} wrap="wrap">
              <Box minW="200px">
                <Text fontSize="sm" mb={2} fontWeight="medium">
                  Category
                </Text>
                <Select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  placeholder="All Categories"
                >
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </Select>
              </Box>

              <Box minW="200px">
                <Text fontSize="sm" mb={2} fontWeight="medium">
                  Sort by
                </Text>
                <Select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <option value="name">Name (A-Z)</option>
                  <option value="price-low">Price (Low to High)</option>
                  <option value="price-high">Price (High to Low)</option>
                  <option value="category">Category</option>
                </Select>
              </Box>
            </HStack>
          </VStack>
        </Box>

        {/* Results Summary */}
        <Box>
          <Text color="gray.600">
            Showing {filteredAndSortedProducts.length} of {state.products.length} products
            {filterCategory && ` in "${filterCategory}"`}
            {searchTerm && ` matching "${searchTerm}"`}
          </Text>
        </Box>

        {/* Products Grid */}
        {filteredAndSortedProducts.length > 0 ? (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3, xl: 4 }} spacing={6}>
            {filteredAndSortedProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onProductClick={handleProductClick}
              />
            ))}
          </SimpleGrid>
        ) : (
          <Box textAlign="center" py={12}>
            <Text fontSize="lg" color="gray.600" mb={4}>
              No products found
            </Text>
            <Text color="gray.500">
              Try adjusting your search terms or filters
            </Text>
          </Box>
        )}
      </VStack>
    </Container>
  )
}
