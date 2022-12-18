
from django.shortcuts import render,get_object_or_404,redirect
from django.http import JsonResponse
import datetime
import json
from .models import  *
from .utils import *
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


#
def main(request):
    

    products = Product.objects.all()
    context = {"prod":products}
    return render(request, 'store/main.html', context)


def store(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {"products":products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items':items,'order':order,'cartItems':cartItems}

    return render(request,'store/cart.html',context)

def checkout(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items':items,'order':order,'cartItems':cartItems}

    return render(request,'store/checkout.html',context)

def product_detail(request, pk):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    template_name = 'store/product_detail.html'
    product = get_object_or_404(Product, pk=pk)
    context = {'product': product,'cartItems':cartItems}
    return render(request, template_name,context)

def search(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method == "POST":
        search = request.POST['search']
        products = Product.objects.filter(name__contains=search)
        return render(request, "store/search.html", {'search':search, 'products':products, 'cartItems':cartItems})
    else:
        return render(request, "store/search.html")


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action :', action)
    print('productId :',productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action =='add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
        
    return JsonResponse('item was added',safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        

        
    else:
        print("COOKIES:", request.COOKIES)
        name = data['form']['name']
        email = data['form']['email']

        cookieData = cookieCart(request)
        items = cookieData['items']

        customer, created  = Customer.objects.get_or_create(
            email = email,
            )
        customer.name = name
        customer.save()

        order = Order.objects.create(
            customer = customer,
            complete = False,
            )

        for item in items:
            product = Product.objects.get(id=item['product']['id'])
            orderItem = OrderItem.objects.create(
                product = product,
                order = order,
                quantity = item['quantity']
                )
        
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
        customer = customer,
        order = order,
        address = data['shipping']['address'],
        city = data['shipping']['city'],
        state = data['shipping']['state'],
        zipcode = data['shipping']['zipcode'],
        )


    

    
    return JsonResponse('payment submitted',safe=False)

def register(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method=="POST":   
            username = request.POST['username']
            full_name=request.POST['full_name']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            
            email = request.POST['email']

            if password1 != password2:
                alert = True
                return render(request, "store/register.html", {'alert':alert})
            
            user = User.objects.create_user(username=username, password=password1, email=email)
            customers = Customer.objects.create(user=user, name=full_name, email=email)
            user.save()
            customers.save()
            return render(request, "store/register.html")
    return render(request, "store/register.html", {'cartItems':cartItems})

def Login(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                alert = True
                return render(request, "store/login.html", {"alert":alert})
    return render(request, "store/login.html", {'cartItems':cartItems})

def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('store'))
