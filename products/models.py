from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import decimal

# Model for Product Categories (e.g., "Gundam", "Marvel Legends", "Star Wars")
class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_list_by_category', args=[self.slug])


# Model for individual Products (Scale Models, Action Figures)
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False) 

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.id, self.slug])


# Model for the Shopping Cart
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user_cart')
    # CORRECTED: Added unique=True to cart_id
    cart_id = models.CharField(max_length=250, blank=True, unique=True) 
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)
        verbose_name = 'cart'
        verbose_name_plural = 'carts'

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return self.cart_id

# Model for individual items within a Shopping Cart
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'cart item'
        verbose_name_plural = 'cart items'
        unique_together = ('cart', 'product')

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.product.name} in cart {self.cart.cart_id}'


# Model for a customer Order
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'order'
        verbose_name_plural = 'orders'

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        total_cost = decimal.Decimal('0.00')
        for item in self.items.all():
            total_cost += item.get_cost()
        return total_cost


# Model for individual items within an Order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'order item'
        verbose_name_plural = 'order items'

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity
