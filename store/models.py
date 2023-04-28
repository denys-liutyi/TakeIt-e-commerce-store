from django.db import models
from django.urls import reverse

from category.models import Category

# Create your models here.

class Product(models.Model):
    """The model of a product in the store."""
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
        """Simple string representation of the product"""
        if len(self.product_name) < 50:
            return self.product_name
        else:
            return f"{self.product_name[:50]}..."
        

class VariationManager(models.Manager):
    """Functions below bring us colors and sizes"""
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)
    

variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)


class Variation(models.Model):
    """The model of variations of the product (color, size)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    #Make functions in VariationManager working.
    #We make sure that all queries for the Variation model go through the custom manager VariationManager.
    objects = VariationManager()

    def __str__(self):
        """String representation of the model."""
        return self.variation_value