from django.db import models

from store.models import Product, Variation
from accounts.models import Account

# Create your models here.

class Cart(models.Model):
    """Model representing a shopping cart."""
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the Cart object."""
        return self.cart_id
    

class CartItem(models.Model):
    """Model representing an item in a shopping cart."""
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        """Calculates the total price of the same product in the cart."""
        return self.product.price * self.quantity

    def __unicode__(self):
        """Return a string representation of the CartItem object."""
        return self.product