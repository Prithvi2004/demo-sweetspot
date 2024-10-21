from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from sweetspot_pro.settings import EMAIL_HOST_USER
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            customer = Customer.objects.get(email=email, password=password)
            return Response({'message': 'Login Successful'})
        except Customer.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class CakeViewSet(viewsets.ModelViewSet):
    queryset = Cake.objects.all()
    serializer_class = CakeSerializer

class CakeCustomizationViewSet(viewsets.ModelViewSet):
    queryset = CakeCustomization.objects.all()
    serializer_class = CakeCustomizationSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def create(self, request, *args, **kwargs):
        customer_id = request.data.get('customer')
        
        # Check if customer already has an active cart
        existing_cart = Cart.objects.filter(
            customer_id=customer_id, 
            is_active=True
        ).first()
        
        if existing_cart:
            return Response(
                CartSerializer(existing_cart).data,
                status=status.HTTP_200_OK
            )

        # If no active cart exists, create a new one
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        try:
            cart = self.get_object()
            
            # Check if cart is active
            if not cart.is_active:
                return Response(
                    {'error': 'This cart is no longer active'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cake_id = request.data.get('cake_id')
            quantity = request.data.get('quantity', 1)
            customization_data = request.data.get('customization')

            # Get the cake
            cake = get_object_or_404(Cake, id=cake_id)
            
            # Check if cake is available
            if not cake.available:
                return Response(
                    {'error': 'This cake is not available'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create customization if provided
            customization = None
            if customization_data:
                customization = CakeCustomization.objects.create(
                    cake=cake,
                    customer=cart.customer,
                    **customization_data
                )

            # Create or update cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                cake=cake,
                defaults={
                    'quantity': quantity,
                    'customization': customization
                }
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response(
                CartSerializer(cart).data,
                status=status.HTTP_200_OK
            )

        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        customer_id = request.data.get('customer_id')
        payment_method = request.data.get('payment_method', 'cod')

        try:
            # Get customer and their active cart
            customer = get_object_or_404(Customer, id=customer_id)
            cart = Cart.objects.get(customer=customer, is_active=True)

            # Check if cart has items
            if not cart.items.exists():
                return Response(
                    {'error': 'Cart is empty'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Calculate total price from cart items
            total_price = cart.total_amount

            # Create the order
            order = Order.objects.create(
                customer=customer,
                total_price=total_price,
                delivery_address=customer.address,
                payment_method=payment_method
            )

            # Process each cart item
            for cart_item in cart.items.all():
                # Add the cake to order items
                order.items.add(cart_item.cake)
                
                # If item has customization, link it to the order
                if cart_item.customization:
                    # Create a new customization for the order
                    order_customization = CakeCustomization.objects.create(
                        message=cart_item.customization.message,
                        egg_version=cart_item.customization.egg_version,
                        toppings=cart_item.customization.toppings,
                        shape=cart_item.customization.shape,
                        cake=cart_item.cake,
                        customer=customer
                    )
                    order.cake_customization = order_customization
                    order.save()

            # Send email notification
            try:
                send_mail(
                    'Order Confirmation',
                    'Payment Successful! Your order has been placed',
                    EMAIL_HOST_USER,
                    [customer.email],
                    fail_silently=True,
                )
            except Exception as e:
                # Log the error but don't fail the order
                print(f"Email sending failed: {str(e)}")

            # Clear the cart
            cart.items.all().delete()
            cart.is_active = False
            cart.save()

            # Create a new active cart for the customer
            Cart.objects.create(customer=customer)

            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )

        except Cart.DoesNotExist:
            return Response(
                {'error': 'No active cart found for this customer'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'])
    def update_payment(self, request, pk=None):
        order = self.get_object()
        order.payment_status = request.data.get('payment_status', order.payment_status)
        order.payment_method = request.data.get('payment_method', order.payment_method)
        order.save()
        return Response(OrderSerializer(order).data)