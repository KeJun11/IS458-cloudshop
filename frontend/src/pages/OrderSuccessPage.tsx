import {
  Container,
  VStack,
  Heading,
  Text,
  Button,
  Box,
  Icon,
  useColorModeValue,
} from "@chakra-ui/react";
import { FaCheckCircle } from "react-icons/fa";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useEffect } from "react";
import { useApp } from "../contexts/AppContext";

export function OrderSuccessPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { actions } = useApp();
  const bg = useColorModeValue("white", "gray.800");

  const sessionId = searchParams.get("session_id");
  const orderId = searchParams.get("order_id");

  useEffect(() => {
    // Clear cart when user lands on success page
    actions.clearCart();
  }, [actions]);

  return (
    <Container maxW="2xl" py={16}>
      <VStack spacing={8} align="center">
        <Box
          bg={bg}
          p={12}
          borderRadius="2xl"
          borderWidth="1px"
          textAlign="center"
          w="full"
        >
          <VStack spacing={6}>
            <Icon as={FaCheckCircle} w={20} h={20} color="green.500" />

            <VStack spacing={2}>
              <Heading size="xl" color="green.500">
                Payment Successful! 🎉
              </Heading>
              <Text fontSize="lg" color="gray.600">
                Thank you for your order!
              </Text>
            </VStack>

            <VStack spacing={2} pt={4}>
              {orderId && (
                <Text fontSize="sm" color="gray.600">
                  Order ID: <strong>{orderId.substring(0, 8)}...</strong>
                </Text>
              )}
              {sessionId && (
                <Text fontSize="xs" color="gray.500">
                  Payment ID: {sessionId.substring(0, 20)}...
                </Text>
              )}
            </VStack>

            <VStack spacing={4} pt={6} w="full">
              <Text fontSize="md" color="gray.700" textAlign="center">
                Your order has been processed successfully!
                <br />
                You will receive a confirmation email shortly.
              </Text>

              <VStack spacing={3} pt={4} w="full">
                <Button
                  size="lg"
                  colorScheme="brand"
                  w="full"
                  onClick={() => navigate("/")}
                >
                  Continue Shopping
                </Button>

                <Button
                  size="md"
                  variant="outline"
                  onClick={() => navigate("/products")}
                >
                  View All Products
                </Button>
              </VStack>
            </VStack>
          </VStack>
        </Box>

        <VStack spacing={3} pt={4}>
          <Text fontSize="sm" color="gray.600" textAlign="center">
            Check your email for order details and tracking information.
          </Text>
          <Text fontSize="xs" color="gray.500">
            Questions? Contact us at support@cloudshop.com
          </Text>
        </VStack>
      </VStack>
    </Container>
  );
}
