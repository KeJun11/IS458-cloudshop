import {
  Container,
  VStack,
  HStack,
  Text,
  Box,
  Heading,
  Button,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Divider,
  Alert,
  AlertIcon,
  useColorModeValue,
  useToast,
  SimpleGrid,
} from "@chakra-ui/react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../contexts/AppContext";
import { apiService } from "../services/api";

interface ShippingInfo {
  name: string;
  email: string;
  address: string;
  city: string;
  zipCode: string;
  phone: string;
}

export function CheckoutPage() {
  const { state, actions } = useApp();
  const navigate = useNavigate();
  const toast = useToast();
  const bg = useColorModeValue("gray.50", "gray.900");
  const [isProcessing, setIsProcessing] = useState(false);

  const [shippingInfo, setShippingInfo] = useState<ShippingInfo>({
    name: state.user?.name || "",
    email: state.user?.email || "",
    address: "",
    city: "",
    zipCode: "",
    phone: "",
  });

  const cartItems = state.cart.items
    .map((item) => ({
      item,
      product: state.products.find((p) => p.id === item.productId)!,
    }))
    .filter(({ product }) => product);

  const subtotal = state.cart.total;
  const tax = subtotal * 0.08;
  const total = subtotal + tax;

  const handleInputChange = (field: keyof ShippingInfo, value: string) => {
    setShippingInfo((prev) => ({ ...prev, [field]: value }));
  };

  const handlePlaceOrder = async () => {
    // Validate form
    const requiredFields: (keyof ShippingInfo)[] = [
      "name",
      "email",
      "address",
      "city",
      "zipCode",
    ];
    const missingFields = requiredFields.filter(
      (field) => !shippingInfo[field].trim()
    );

    if (missingFields.length > 0) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    if (cartItems.length === 0) {
      toast({
        title: "Empty Cart",
        description: "Your cart is empty",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsProcessing(true);

    try {
      // Call the API to create the order
      const orderData = {
        userId: state.user!.id,
        items: state.cart.items.map((item) => ({
          productId: item.productId,
          quantity: item.quantity,
          product: state.products.find((p) => p.id === item.productId),
        })),
        total,
        shippingInfo,
      };

      const result = await apiService.createOrder(orderData);
      console.log("Order created:", result);

      // Clear cart after successful order
      actions.clearCart();

      toast({
        title: "Order Placed Successfully!",
        description: "You will receive a confirmation email shortly",
        status: "success",
        duration: 5000,
        isClosable: true,
      });

      // Navigate to success page or home
      navigate("/", { replace: true });
    } catch (error) {
      console.error("Order creation failed:", error);
      toast({
        title: "Order Failed",
        description:
          "There was an error processing your order. Please try again.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsProcessing(false);
    }
  };

  if (cartItems.length === 0) {
    return (
      <Container maxW="4xl" py={8}>
        <VStack spacing={8} align="center" py={12}>
          <Heading size="lg">No Items to Checkout</Heading>
          <Text fontSize="lg" color="gray.600" textAlign="center">
            Your cart is empty. Add some items before proceeding to checkout.
          </Text>
          <Button
            size="lg"
            colorScheme="brand"
            onClick={() => navigate("/products")}
          >
            Start Shopping
          </Button>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="6xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Heading size="xl">Checkout</Heading>

        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
          {/* Shipping Information */}
          <Box>
            <VStack spacing={6} align="stretch">
              <Heading size="md">Shipping Information</Heading>

              <VStack spacing={4} align="stretch">
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  <FormControl isRequired>
                    <FormLabel>Full Name</FormLabel>
                    <Input
                      value={shippingInfo.name}
                      onChange={(e) =>
                        handleInputChange("name", e.target.value)
                      }
                      placeholder="Enter your full name"
                    />
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel>Email</FormLabel>
                    <Input
                      type="email"
                      value={shippingInfo.email}
                      onChange={(e) =>
                        handleInputChange("email", e.target.value)
                      }
                      placeholder="Enter your email"
                    />
                  </FormControl>
                </SimpleGrid>

                <FormControl isRequired>
                  <FormLabel>Address</FormLabel>
                  <Textarea
                    value={shippingInfo.address}
                    onChange={(e) =>
                      handleInputChange("address", e.target.value)
                    }
                    placeholder="Enter your full address"
                    rows={3}
                  />
                </FormControl>

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  <FormControl isRequired>
                    <FormLabel>City</FormLabel>
                    <Input
                      value={shippingInfo.city}
                      onChange={(e) =>
                        handleInputChange("city", e.target.value)
                      }
                      placeholder="Enter your city"
                    />
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel>ZIP Code</FormLabel>
                    <Input
                      value={shippingInfo.zipCode}
                      onChange={(e) =>
                        handleInputChange("zipCode", e.target.value)
                      }
                      placeholder="Enter ZIP code"
                    />
                  </FormControl>
                </SimpleGrid>

                <FormControl>
                  <FormLabel>Phone Number</FormLabel>
                  <Input
                    type="tel"
                    value={shippingInfo.phone}
                    onChange={(e) => handleInputChange("phone", e.target.value)}
                    placeholder="Enter your phone number"
                  />
                </FormControl>
              </VStack>
            </VStack>
          </Box>

          {/* Order Summary */}
          <Box>
            <VStack spacing={6} align="stretch">
              <Heading size="md">Order Summary</Heading>

              <Box bg={bg} p={6} borderRadius="lg" borderWidth="1px">
                <VStack spacing={4} align="stretch">
                  {/* Order Items */}
                  <VStack spacing={3} align="stretch">
                    {cartItems.map(({ item, product }) => (
                      <HStack key={item.productId} justify="space-between">
                        <VStack align="start" spacing={0}>
                          <Text fontWeight="medium" fontSize="sm">
                            {product.name}
                          </Text>
                          <Text fontSize="xs" color="gray.600">
                            Qty: {item.quantity} × ${product.price.toFixed(2)}
                          </Text>
                        </VStack>
                        <Text fontWeight="medium">
                          ${(product.price * item.quantity).toFixed(2)}
                        </Text>
                      </HStack>
                    ))}
                  </VStack>

                  <Divider />

                  {/* Totals */}
                  <VStack spacing={2} align="stretch">
                    <HStack justify="space-between">
                      <Text>Subtotal:</Text>
                      <Text>${subtotal.toFixed(2)}</Text>
                    </HStack>

                    <HStack justify="space-between">
                      <Text>Shipping:</Text>
                      <Text>Free</Text>
                    </HStack>

                    <HStack justify="space-between">
                      <Text>Tax:</Text>
                      <Text>${tax.toFixed(2)}</Text>
                    </HStack>

                    <Divider />

                    <HStack justify="space-between">
                      <Text fontSize="lg" fontWeight="bold">
                        Total:
                      </Text>
                      <Text fontSize="lg" fontWeight="bold" color="brand.500">
                        ${total.toFixed(2)}
                      </Text>
                    </HStack>
                  </VStack>

                  <VStack spacing={3} pt={4}>
                    <Button
                      size="lg"
                      colorScheme="brand"
                      w="full"
                      onClick={handlePlaceOrder}
                      isLoading={isProcessing}
                      loadingText="Processing Order..."
                    >
                      Place Order
                    </Button>

                    <Button
                      size="lg"
                      variant="outline"
                      w="full"
                      onClick={() => navigate("/cart")}
                      isDisabled={isProcessing}
                    >
                      Back to Cart
                    </Button>
                  </VStack>
                </VStack>
              </Box>

              <Alert status="info">
                <AlertIcon />
                <VStack align="start" spacing={1}>
                  <Text fontWeight="medium" fontSize="sm">
                    Secure Checkout
                  </Text>
                  <Text fontSize="xs">
                    Your order will be processed through our secure cloud
                    infrastructure.
                  </Text>
                </VStack>
              </Alert>
            </VStack>
          </Box>
        </SimpleGrid>
      </VStack>
    </Container>
  );
}
