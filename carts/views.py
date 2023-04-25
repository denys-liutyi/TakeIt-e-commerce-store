from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from carts.models import Cart, CartItem
from django.http import HttpResponse

# Create your views here.

def _cart_id(request):
    """Returns cart id from session. Creates new cart if not found."""
    cart = request.session.session_key  #Session key is session id
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    """Adds selected product to cart or increments quantity if product is already in cart."""
    #Get the product.
    product = Product.objects.get(id=product_id)
    try:
        #Get the cart using the cart id which is present in the session (in cookies)
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    #Combine the product and the cart to get the cart item.
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
        cart_item.save()

    return redirect('carts:cart')


def remove_cart(request, product_id):
    """Decrements quantity of the product if it is already in cart 
    or removes selected product from cart if the quantity is less than 1."""
    #Get the cart using the cart id which is present in the session (in cookies).
    cart = Cart.objects.get(cart_id=_cart_id(request))
    #Get the product.
    product = get_object_or_404 (Product, id=product_id)
    #Bring the cart item.
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('carts:cart')


def remove_cart_item(request, product_id):
    """Removes selected product from cart."""
    #Get the cart using the cart id which is present in the session (in cookies).
    cart = Cart.objects.get(cart_id=_cart_id(request))
    #Get the product.
    product = get_object_or_404 (Product, id=product_id)
    #Bring the cart item.
    cart_item = CartItem.objects.get(product=product, cart=cart)

    cart_item.delete()

    return redirect('carts:cart')


def cart(request, total=0, quantity=0, cart_items=None, tax=0, grand_total=0):
    """
    Renders cart page and displays the cart items info. Retrieves the cart from the session,
    gets all active cart items for the cart, calculates all and passes it to the template.
    If no cart exists in the session, an empty cart is displayed. In case of errors, they are ignored and an empty cart is displayed.
    """
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            tax = total * 0.2
            grand_total = total + tax
    except Cart.DoesNotExist:
        pass #just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': round(tax, 2), #Rounds the tax value to 2 digits after period
        'grand_total': grand_total,
    }

    return render (request, 'store/cart.html', context)