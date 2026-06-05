from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Restaurant, MenuItem, Cart, Order, OrderItem

def home(request):
    query = request.GET.get('q', '')
    if query:
        restaurants = Restaurant.objects.filter(name__icontains=query, is_open=True)
    else:
        restaurants = Restaurant.objects.filter(is_open=True)
    return render(request, 'restaurant/home.html', {'restaurants': restaurants, 'query': query})

def menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = MenuItem.objects.filter(restaurant=restaurant, is_available=True)
    return render(request, 'restaurant/menu.html', {'restaurant': restaurant, 'menu_items': menu_items})

@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, item=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('menu', restaurant_id=item.restaurant.id)

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'restaurant/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        return redirect('cart')
    total = sum(item.total_price() for item in cart_items)
    order = Order.objects.create(user=request.user, total=total, is_confirmed=True)
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            item=cart_item.item,
            quantity=cart_item.quantity,
            price=cart_item.item.price
        )
    cart_items.delete()
    return redirect('order_confirmation', order_id=order.id)

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'restaurant/order_confirmation.html', {'order': order, 'order_items': order_items})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'restaurant/order_history.html', {'orders': orders})
