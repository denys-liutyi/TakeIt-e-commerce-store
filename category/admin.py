from django.contrib import admin

from .models import Category

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    """Defines admin interface for Category model with prepopulated slug field and customized list view display"""
    prepopulated_fields = {'slug': ('category_name', )}
    list_display = ('category_name', 'slug')


admin.site.register(Category, CategoryAdmin)