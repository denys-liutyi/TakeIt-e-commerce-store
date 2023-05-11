from django.shortcuts import render, redirect
from django.http import HttpResponse
import datetime
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product

# Create your views here.

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    #Store transaction details inside the Payment model.
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment #Update the payment field in the Order model.
    order.is_ordered = True
    order.save()

    #Move cart items to Order Product table.
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
        #We don't assign directly the variation field above, because it is a ManyToMany field. First we need to save the orderproduct object and then access the product variation.
        
        #Handle variations below.
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id) #The save() method in line 42 generated the orderproduct ID.
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        #Reduce the quantity of sold products.
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    #Clear the cart.
    CartItem.objects.filter(user=request.user).delete()

    #Send order details to customers email.
    mail_subject = 'Thank you for your order!'
    #Pass the content we are going to send in an email:
    message = render_to_string('orders/order_received_email.html',{
        'user': request.user,
        'order': order,
    }) 
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    #Send order number and transaction id back to sendData method (in payments.html) via JsonResponse.

    return render(request, 'orders/payments.html')


def place_order(request, total=0, quantity=0):
    current_user = request.user

    #If the cart count is less or equal to 0, redirect user to the shop.
    cart_items = CartItem.objects.filter(user=request.user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store:store')
    
    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = round(total * 0.2, 2) #Round tax value.
    #tax = round(tax, 2)
    grand_total = total + tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            #Store all the billing information inside Order table.
            data = Order() #The instance of the order.

            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR') #Get user's IP.
            data.save()
            
            #Generate order number.
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #Example: 20230419
            order_number = current_date + str(data.id) #id is automatically generated.
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }

            return render(request, 'orders/payments.html', context)
        
        else:
            return redirect('carts:checkout')
