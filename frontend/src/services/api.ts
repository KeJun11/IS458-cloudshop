// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://api.your-domain.com'

// Types
export interface Product {
  id: string
  name: string
  description: string
  price: number
  category: string
  imageUrl: string
  stock: number
}

export interface CartItem {
  productId: string
  quantity: number
  product?: Product
}

export interface Cart {
  userId: string
  items: CartItem[]
  total: number
}

export interface Order {
  id: string
  userId: string
  items: CartItem[]
  total: number
  status: 'PENDING' | 'PROCESSED' | 'SHIPPED' | 'DELIVERED'
  createdAt: string
  shippingInfo: {
    name: string
    email: string
    address: string
    city: string
    zipCode: string
  }
}

export interface UserInteraction {
  userId: string
  productId: string
  eventType: 'product-view' | 'add-to-cart' | 'purchase'
  productType: string
  timestamp: string
}

// API Service Class
class ApiService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      // Fetching the product, edit this to change the point
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Product APIs
  async getProducts(): Promise<Product[]> {
    return this.request<Product[]>('/products')
  }

  async getProduct(id: string): Promise<Product> {
    return this.request<Product>(`/products/${id}`)
  }

  // Cart APIs
  async getCart(userId: string): Promise<Cart> {
    return this.request<Cart>(`/cart?userId=${userId}`)
  }

  async addToCart(userId: string, productId: string, quantity: number): Promise<Cart> {
    return this.request<Cart>('/cart', {
      method: 'POST',
      body: JSON.stringify({ userId, productId, quantity }),
    })
  }

  async updateCartItem(userId: string, productId: string, quantity: number): Promise<Cart> {
    return this.request<Cart>('/cart', {
      method: 'PUT',
      body: JSON.stringify({ userId, productId, quantity }),
    })
  }

  async removeFromCart(userId: string, productId: string): Promise<Cart> {
    return this.request<Cart>('/cart', {
      method: 'DELETE',
      body: JSON.stringify({ userId, productId }),
    })
  }

  // Order APIs
  async createOrder(orderData: Omit<Order, 'id' | 'status' | 'createdAt'>): Promise<{ orderId: string; status: string }> {
    return this.request<{ orderId: string; status: string }>('/orders', {
      method: 'POST',
      body: JSON.stringify(orderData),
    })
  }

  async getOrders(userId: string): Promise<Order[]> {
    return this.request<Order[]>(`/orders?userId=${userId}`)
  }

  async getOrder(orderId: string): Promise<Order> {
    return this.request<Order>(`/orders/${orderId}`)
  }

  // User Interaction APIs (for recommendations)
  async trackEvent(interaction: Omit<UserInteraction, 'timestamp'>): Promise<void> {
    return this.request<void>('/events', {
      method: 'POST',
      body: JSON.stringify({
        ...interaction,
        timestamp: new Date().toISOString(),
      }),
    })
  }

  async getRecommendations(userId: string): Promise<Product[]> {
    return this.request<Product[]>(`/recommendations?userId=${userId}`)
  }
}

// Create and export a singleton instance
export const apiService = new ApiService()

// Mock data for development (will be replaced by actual API calls)
export const mockProducts: Product[] = [
  {
    id: 'prod-1',
    name: 'Wireless Bluetooth Headphones',
    description: 'High-quality wireless headphones with noise cancellation',
    price: 199.99,
    category: 'Electronics',
    imageUrl: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500',
    stock: 50,
  },
  {
    id: 'prod-2',
    name: 'Smart Watch',
    description: 'Feature-rich smartwatch with health tracking',
    price: 299.99,
    category: 'Electronics',
    imageUrl: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500',
    stock: 30,
  },
  {
    id: 'prod-3',
    name: 'Laptop Backpack',
    description: 'Durable laptop backpack with multiple compartments',
    price: 79.99,
    category: 'Accessories',
    imageUrl: 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500',
    stock: 100,
  },
  {
    id: 'prod-4',
    name: 'Wireless Mouse',
    description: 'Ergonomic wireless mouse with precision tracking',
    price: 49.99,
    category: 'Electronics',
    imageUrl: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500',
    stock: 75,
  },
  {
    id: 'prod-5',
    name: 'USB-C Hub',
    description: 'Multi-port USB-C hub with HDMI and charging support',
    price: 89.99,
    category: 'Electronics',
    imageUrl: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500',
    stock: 40,
  },
  {
    id: 'prod-6',
    name: 'Portable Charger',
    description: '20000mAh portable battery pack with fast charging',
    price: 39.99,
    category: 'Electronics',
    imageUrl: 'https://images.unsplash.com/photo-1609592806955-d5b6c3b2e3c5?w=500',
    stock: 60,
  },
]
