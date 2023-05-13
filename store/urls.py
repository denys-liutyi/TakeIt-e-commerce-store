"""Defines URL patterns for the APP store"""

from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    #store page which shows all available products
    path('', views.store, name='store'),
    #Shows all products of selected category
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    #Shows product details
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
]