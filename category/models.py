from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    """Product category"""
    category_name           = models.CharField(max_length=50, unique=True)
    slug                    = models.SlugField(max_length=50, unique=True)
    category_description    = models.TextField(blank=True)
    category_image          = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        """Create a URL for the particular category using the slug. This function is used in a template NAVBAR"""
        return reverse('store:products_by_category', args=[self.slug])

    def __str__ (self):
        """Returns string representation of the model"""
        return self.category_name
    