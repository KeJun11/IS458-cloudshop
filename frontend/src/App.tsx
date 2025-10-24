import { Box } from '@chakra-ui/react'
import { Routes, Route } from 'react-router-dom'
import { AppProvider } from './contexts/AppContext'
import { Header } from './components/Header'
import { HomePage } from './pages/HomePage'
import { ProductsPage } from './pages/ProductsPage'
import { ProductDetailPage } from './pages/ProductDetailPage'
import { CartPage } from './pages/CartPage'
import { CheckoutPage } from './pages/CheckoutPage'

function App() {
  return (
    <AppProvider>
      <Box minH="100vh" bg="gray.50">
        <Header />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/product/:id" element={<ProductDetailPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
        </Routes>
      </Box>
    </AppProvider>
  )
}

export default App
