from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q


from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id

# Create your views here.

def store(request, category_slug=None):
    """Show all products by selected categories of by all categories"""
    categories = None
    products = None

    #Bring in categories if found or raise 404 error
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=categories, is_available=True)

        #Paginator to display 6 products on page.
        paginator = Paginator(products, 6) #Show 6 products per page.
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        
        products_count = products.count()
        
    #The store page, which shows all available in stock products (if there is no slug)
    else:    
        products = Product.objects.all().filter(is_available=True).order_by('id')

        #Paginator to display 6 products on page.
        paginator = Paginator(products, 6) #Show 6 products per page.
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

        products_count = products.count()

    context = {
        'products': paged_products, #We pass only 6 products to display, which we got using paginator.
        'products_count': products_count,
    }
    return render (request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    """Show a single product details"""
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        #In brackets 'cart' is a foreign key of CarItems, so with the cart we access the cart_id (check carts:models.py),
        #that's why we put '__' (double underscore).
        #'exists()' will return True of this query if the product is in the cart
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists() 
        
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    """   """
    #Check if there is a keyword in the get request (in the URL) and store the value of 'keyword' in the variable.
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']

        if keyword:
            #icontains (below) searches for anything related to keyword in product description.
            products = Product.objects.order_by('-created_date').filter(
                Q(product_description__icontains=keyword) | Q(product_name__icontains=keyword)
                ) 
            products_count = products.count()

    context = {
        'products': products,
        'products_count': products_count,
    }
    return render (request, 'store/store.html', context)