from django.contrib import admin

from .models import Product, Variation

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    """Defines admin interface for Product model with prepopulated slug field and customized list view display"""
    prepopulated_fields = {'slug': ('product_name', )}
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')


class VariationAdmin(admin.ModelAdmin):
    """
    Defines admin interface for Variation model,
    customized list view display and editable column 'is active'
    and added filter list"""
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)