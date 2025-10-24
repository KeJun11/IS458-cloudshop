# CloudShop - E-Commerce Frontend

A modern, responsive e-commerce frontend built with React, TypeScript, and Chakra UI. This application is designed to integrate seamlessly with a cloud-based backend infrastructure using AWS services.

## Features

- **Modern UI**: Built with Chakra UI for a beautiful, accessible interface
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Product Browsing**: Browse products with search, filtering, and sorting capabilities
- **Shopping Cart**: Add, remove, and modify items in your cart
- **Checkout Process**: Complete order placement with shipping information
- **Product Recommendations**: View personalized product recommendations
- **State Management**: Efficient state management with React Context
- **TypeScript**: Full TypeScript support for better development experience

## Technology Stack

- **React 18** - Modern React with hooks and functional components
- **TypeScript** - Type-safe development
- **Chakra UI** - Component library for beautiful UI
- **React Router** - Client-side routing
- **Vite** - Fast build tool and development server

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Header.tsx      # Navigation header with cart indicator
│   ├── ProductCard.tsx # Product display card
│   └── CartItem.tsx    # Shopping cart item component
├── pages/              # Page components
│   ├── HomePage.tsx    # Landing page with featured products
│   ├── ProductsPage.tsx # Product listing with filters
│   ├── ProductDetailPage.tsx # Individual product details
│   ├── CartPage.tsx    # Shopping cart management
│   └── CheckoutPage.tsx # Order placement
├── contexts/           # React Context for state management
│   └── AppContext.tsx  # Global app state and actions
├── services/           # API service layer
│   └── api.ts         # API calls and data types
└── theme.ts           # Chakra UI theme configuration
```

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Navigate to the project directory:
   ```bash
   cd ecommerce-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and visit `http://localhost:5173`

## Backend Integration

This frontend is designed to work with a cloud-based backend. The API service layer (`src/services/api.ts`) contains all the necessary functions to integrate with your backend:

### API Endpoints Expected

- `GET /products` - Fetch all products
- `GET /products/:id` - Fetch single product
- `POST /cart` - Add item to cart
- `PUT /cart` - Update cart item
- `DELETE /cart` - Remove item from cart
- `POST /orders` - Create new order
- `GET /orders` - Fetch user orders
- `POST /events` - Track user interactions
- `GET /recommendations` - Get personalized recommendations

### Environment Variables

Create a `.env` file in the root directory:

```env
REACT_APP_API_URL=https://your-api-gateway-url.com
```

### Switching from Mock Data to Real API

The application currently uses mock data for development. To switch to real API calls:

1. Set the `REACT_APP_API_URL` environment variable
2. In `src/contexts/AppContext.tsx`, uncomment the API calls and comment out the mock data usage
3. Ensure your backend API matches the expected interface defined in `src/services/api.ts`

## Features in Detail

### Product Management
- Browse products with pagination
- Search products by name, description, or category
- Filter by category
- Sort by name, price, or category
- View detailed product information

### Shopping Cart
- Add products to cart with quantity selection
- Update item quantities
- Remove items from cart
- Persistent cart state during session
- Real-time cart total calculation

### Order Processing
- Secure checkout process
- Shipping information collection
- Order summary and confirmation
- Integration ready for payment processing

### User Experience
- Responsive design for all devices
- Loading states and error handling
- Toast notifications for user actions
- Smooth navigation and transitions
- Accessibility features built-in

## Customization

### Theme
Modify `src/theme.ts` to customize colors, fonts, and component styles.

### Components
All components are built with Chakra UI and can be easily customized by modifying their props or extending the theme.

### API Integration
The API service layer is abstracted in `src/services/api.ts`, making it easy to modify endpoints or add new functionality.

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory, ready for deployment to any static hosting service or CDN.

## Deployment

This application is designed to be deployed as static files and can be hosted on:
- AWS S3 + CloudFront
- Vercel
- Netlify
- Any static hosting service

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.