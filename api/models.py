# models.py
from django.db import models
from django.utils import timezone

class Customer(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    created_at = models.DateTimeField(default=timezone.now)  

class Cake(models.Model):
    name = models.CharField(max_length=200)
    flavour = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)  # Made optional
    image = models.ImageField(upload_to='cakes/', blank=True)  # Made optional
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)  

class CakeCustomization(models.Model):
    message = models.CharField(max_length=200, blank=True)
    egg_version = models.BooleanField(default=True)
    toppings = models.CharField(max_length=200, blank=True)  # Made optional
    shape = models.CharField(max_length=50, default='round')  
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)  

class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='items')
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    customization = models.OneToOneField(
        CakeCustomization, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)  
    @property
    def subtotal(self):
        return self.cake.price * self.quantity

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)  
    updated_at = models.DateTimeField(auto_now=True)  
    is_active = models.BooleanField(default=True)  # Added to track active carts

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    PAYMENT_METHOD = (
        ('cod', 'Cash on Delivery'),
        ('card', 'Card'),
        ('upi', 'UPI'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cake_customization = models.ForeignKey(
        CakeCustomization, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    items = models.ManyToManyField(Cake)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00  
    )
    order_date = models.DateTimeField(default=timezone.now)  
    delivery_address = models.TextField()
    order_status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS, 
        default='pending'
    )
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD,
        default='cod'  
    )
    created_at = models.DateTimeField(default=timezone.now)  
    updated_at = models.DateTimeField(auto_now=True)  