import React, {
  createContext,
  useContext,
  useReducer,
  useEffect,
  type ReactNode,
} from "react";
import {
  type Product,
  type Cart,
  type CartItem,
  apiService,
} from "../services/api";

// Types
interface User {
  id: string;
  name: string;
  email: string;
}

interface AppState {
  user: User | null;
  products: Product[];
  cart: Cart;
  loading: boolean;
  error: string | null;
  recommendations: Product[];
}

type AppAction =
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_ERROR"; payload: string | null }
  | { type: "SET_USER"; payload: User | null }
  | { type: "SET_PRODUCTS"; payload: Product[] }
  | { type: "SET_CART"; payload: Cart }
  | { type: "ADD_TO_CART"; payload: { product: Product; quantity: number } }
  | {
      type: "UPDATE_CART_ITEM";
      payload: { productId: string; quantity: number };
    }
  | { type: "REMOVE_FROM_CART"; payload: string }
  | { type: "CLEAR_CART" }
  | { type: "SET_RECOMMENDATIONS"; payload: Product[] };

// Initial state
const initialState: AppState = {
  user: { id: "user-demo", name: "Demo User", email: "demo@example.com" }, // Demo user for development
  products: [],
  cart: {
    userId: "user-demo",
    items: [],
    total: 0,
  },
  loading: false,
  error: null,
  recommendations: [],
};

// Reducer
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case "SET_LOADING":
      return { ...state, loading: action.payload };

    case "SET_ERROR":
      return { ...state, error: action.payload, loading: false };

    case "SET_USER":
      return { ...state, user: action.payload };

    case "SET_PRODUCTS":
      return { ...state, products: action.payload };

    case "SET_CART":
      return { ...state, cart: action.payload };

    case "ADD_TO_CART": {
      const { product, quantity } = action.payload;
      const existingItemIndex = state.cart.items.findIndex(
        (item) => item.productId === product.id
      );

      let updatedItems: CartItem[];
      if (existingItemIndex >= 0) {
        updatedItems = state.cart.items.map((item, index) =>
          index === existingItemIndex
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      } else {
        updatedItems = [
          ...state.cart.items,
          { productId: product.id, quantity, product },
        ];
      }

      const total = updatedItems.reduce((sum, item) => {
        const itemProduct =
          item.product || state.products.find((p) => p.id === item.productId);
        return sum + (itemProduct ? itemProduct.price * item.quantity : 0);
      }, 0);

      return {
        ...state,
        cart: {
          ...state.cart,
          items: updatedItems,
          total,
        },
      };
    }

    case "UPDATE_CART_ITEM": {
      const { productId, quantity } = action.payload;
      const updatedItems =
        quantity === 0
          ? state.cart.items.filter((item) => item.productId !== productId)
          : state.cart.items.map((item) =>
              item.productId === productId ? { ...item, quantity } : item
            );

      const total = updatedItems.reduce((sum, item) => {
        const itemProduct =
          item.product || state.products.find((p) => p.id === item.productId);
        return sum + (itemProduct ? itemProduct.price * item.quantity : 0);
      }, 0);

      return {
        ...state,
        cart: {
          ...state.cart,
          items: updatedItems,
          total,
        },
      };
    }

    case "REMOVE_FROM_CART": {
      const updatedItems = state.cart.items.filter(
        (item) => item.productId !== action.payload
      );
      const total = updatedItems.reduce((sum, item) => {
        const itemProduct =
          item.product || state.products.find((p) => p.id === item.productId);
        return sum + (itemProduct ? itemProduct.price * item.quantity : 0);
      }, 0);

      return {
        ...state,
        cart: {
          ...state.cart,
          items: updatedItems,
          total,
        },
      };
    }

    case "CLEAR_CART":
      return {
        ...state,
        cart: {
          ...state.cart,
          items: [],
          total: 0,
        },
      };

    case "SET_RECOMMENDATIONS":
      return { ...state, recommendations: action.payload };

    default:
      return state;
  }
}

// Context
const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  actions: {
    loadProducts: () => Promise<void>;
    addToCart: (product: Product, quantity?: number) => Promise<void>;
    updateCartItem: (productId: string, quantity: number) => Promise<void>;
    removeFromCart: (productId: string) => Promise<void>;
    clearCart: () => void;
    trackProductView: (product: Product) => Promise<void>;
    loadRecommendations: () => Promise<void>;
  };
} | null>(null);

// Provider component
export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Actions
  const actions = {
    loadProducts: async () => {
      dispatch({ type: "SET_LOADING", payload: true });
      try {
        // Call the actual API endpoint
        const products = await apiService.getProducts();
        dispatch({ type: "SET_PRODUCTS", payload: products });
      } catch (error) {
        dispatch({ type: "SET_ERROR", payload: "Failed to load products" });
        console.error("Error loading products:", error);
      } finally {
        dispatch({ type: "SET_LOADING", payload: false });
      }
    },

    addToCart: async (product: Product, quantity = 1) => {
      try {
        // Call the actual API endpoint
        if (state.user) {
          const updatedCart = await apiService.addToCart(
            state.user.id,
            product.id,
            quantity
          );
          dispatch({ type: "SET_CART", payload: updatedCart });

          // Don't track add-to-cart for recommendations (keep it simple)
        }
      } catch (error) {
        dispatch({ type: "SET_ERROR", payload: "Failed to add item to cart" });
        console.error("Error adding to cart:", error);
      }
    },

    updateCartItem: async (productId: string, quantity: number) => {
      try {
        if (state.user) {
          const updatedCart = await apiService.updateCartItem(
            state.user.id,
            productId,
            quantity
          );
          dispatch({ type: "SET_CART", payload: updatedCart });
        }
      } catch (error) {
        dispatch({ type: "SET_ERROR", payload: "Failed to update cart item" });
        console.error("Error updating cart item:", error);
      }
    },

    removeFromCart: async (productId: string) => {
      try {
        if (state.user) {
          const updatedCart = await apiService.removeFromCart(
            state.user.id,
            productId
          );
          dispatch({ type: "SET_CART", payload: updatedCart });
        }
      } catch (error) {
        dispatch({
          type: "SET_ERROR",
          payload: "Failed to remove item from cart",
        });
        console.error("Error removing from cart:", error);
      }
    },

    clearCart: () => {
      dispatch({ type: "CLEAR_CART" });
    },

    trackProductView: async (product: Product) => {
      try {
        if (state.user) {
          await apiService.trackEvent({
            userId: state.user.id,
            productId: product.id,
            eventType: "product-view",
            productType: product.category,
          });
        }
      } catch (error) {
        console.error("Error tracking product view:", error);
      }
    },

    loadRecommendations: async () => {
      try {
        if (state.user) {
          const recommendations = await apiService.getRecommendations(
            state.user.id
          );
          dispatch({ type: "SET_RECOMMENDATIONS", payload: recommendations });
        }
      } catch (error) {
        console.error("Error loading recommendations:", error);
      }
    },
  };

  // Load initial data
  useEffect(() => {
    actions.loadProducts();
    actions.loadRecommendations();
  }, []);

  return (
    <AppContext.Provider value={{ state, dispatch, actions }}>
      {children}
    </AppContext.Provider>
  );
}

// Hook to use the context
export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
}
