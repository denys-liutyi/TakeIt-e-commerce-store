from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from carts.models import Cart, CartItem
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.

def _cart_id(request):
    """Returns cart id from session. Creates new cart if not found."""
    cart = request.session.session_key  #Session key is session id
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    """
    Stores the variation of selected product
    and adds it to cart or increments quantity if product is already in cart.
    """
    current_user = request.user
    #Get the product.
    product = Product.objects.get(id=product_id)

    #IF THE USER IS AUTHENTICATED:
    if current_user.is_authenticated:
        #Set an empty list of products with variations.
        product_variation = []

        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                #Check if key, value from the request.POST above 
                #are matching the model values (variation value and category) in Variation model.
                try:
                    #'__iexact' below performs a case-insensitive exact match in the database.
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        #Combine the product and the cart to get the cart item.
        #First check if cart item exists.
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists() #Returns True (there are cart items of the user) or False
        
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user) #Return cart item objects of the user.
            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation)) #It's a query set, so it should be converted to a list.
                id.append(item.id)

            if product_variation in existing_variation_list:
                #Increase cart item quantity.
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1

                item.save()
            else:
                #Create a new cart item.
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()    
                    item.variations.add(*product_variation) #'*' means to add all the variations.

                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )

            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()

        return redirect('carts:cart')

    #IF THE USER IS NOT AUTHENTICATED:
    else:
        #Set an empty list of products with variations.
        product_variation = []

        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                #Check if key, value from the request.POST above 
                #are matching the model values (variation value and category) in Variation model.
                try:
                    #'__iexact' below performs a case-insensitive exact match in the database.
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        try:
            #Get the cart using the cart id which is present in the session (in cookies)
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

        #Combine the product and the cart to get the cart item.
        #First check if cart item exists.
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists() #Returns True (there are cart items) or False
        
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart) #Return cart item objects.
            #existing variations --> database
            #current variation --> product_variation
            #item_id --> database
            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation)) #It's a query set, so it should be converted to a list.
                id.append(item.id)
            print(existing_variation_list)

            if product_variation in existing_variation_list:
                #Increase cart item quantity.
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1

                item.save()
            else:
                #Create a new cart item.
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()    
                    item.variations.add(*product_variation) #'*' means to add all the variations.

                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )

            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()

        return redirect('carts:cart')


def remove_cart(request, product_id, cart_item_id):
    """Decrements quantity of the product if it is already in cart 
    or removes selected product from cart if the quantity is less than 1."""
    #Get the product.
    product = get_object_or_404 (Product, id=product_id)
    #Bring the cart item.
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            #Get the cart using the cart id which is present in the session (in cookies).
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect('carts:cart')


def remove_cart_item(request, product_id, cart_item_id):
    """Removes selected product from cart."""
    #Get the product.
    product = get_object_or_404 (Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        #Get the cart using the cart id which is present in the session (in cookies).
        cart = Cart.objects.get(cart_id=_cart_id(request))
        #Bring the cart item.
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

    cart_item.delete()

    return redirect('carts:cart')


def cart(request, total=0, quantity=0, cart_items=None, tax=0, grand_total=0):
    """
    Renders cart page and displays the cart items info. Retrieves the cart from the session,
    gets all active cart items for the cart, calculates all and passes it to the template.
    If no cart exists in the session, an empty cart is displayed. In case of errors, they are ignored and an empty cart is displayed.
    """
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
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


@login_required(login_url='accounts:login')
def checkout(request, total=0, quantity=0, cart_items=None, tax=0, grand_total=0):
    """
    Handles the checkout process, calculates the total price, quantity, tax, and grand total for the items in the cart.
    """
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
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

    return render(request, 'store/checkout.html', context)