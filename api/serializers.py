from rest_framework import serializers
from .models import *

class CustomerSerializer(serializers.ModelSerializer):
    
    def validate_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("Name should only contain letters.")
        return value

    def validate_email(self, value):
        if not "@" in value:
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number should be 10 digits.")
        return value
    
    def validate_pincode(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Pincode should be 6 digits.")
        return value
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password should be at least 8 characters.")
        return value

    class Meta:
        model = Customer
        fields = '__all__'

class CakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cake
        fields = '__all__'

class CakeCustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CakeCustomization
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'cake', 'quantity', 'customization', 'subtotal']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'items', 'total_amount', 'created_at', 'updated_at']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'