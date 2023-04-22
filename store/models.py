from django.db import models
from django.urls import reverse

from category.models import Category

# Create your models here.

class Product(models.Model):
    """The model of a product in the store"""
    product_name        = models.CharField(max_length=200, unique=True)
    slug                = models.SlugField(max_length=200, unique=True)
    product_description = models.TextField(max_length=500, blank=True)
    price               = models.IntegerField()
    product_images      = models.ImageField(upload_to='photos/products', blank=True)
    stock               = models.IntegerField()
    is_available        = models.BooleanField(default=True)
    category            = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date        = models.DateTimeField(auto_now_add=True)
    modified_date       = models.DateTimeField(auto_now=True)

    def get_url(self):
        """Create a URL for the particular product using the slug"""
        return reverse('store:product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        """Simple string representation of a product"""
        if len(self.product_name) < 50:
            return self.product_name
        else:
            return f"{self.product_name[:50]}..."