from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

from .models import Product, Order


# Create your views here.


def shop_index(request: HttpRequest) -> HttpResponse:
    products = [
        ('Laptop', 1999),
        ('Desktop', 2999),
        ('Smartphone', 999),
    ]
    context = {'time_running': default_timer(),
               'products': products,
               }
    return render(request, 'shopapp/shop-index.html', context=context)


def groups_list(request: HttpRequest) -> HttpResponse:
    context = {
        'groups': Group.objects.prefetch_related('permissions').all(),
    }
    return render(request, 'shopapp/groups-list.html', context=context)


def products_list(request: HttpRequest) -> HttpResponse:
    context = {
        'products': Product.objects.all(),
    }
    return render(request, 'shopapp/products-list.html', context=context)


def orders_list(request: HttpRequest) -> HttpResponse:
    context = {
        'orders': Order.objects.select_related('user').prefetch_related('products').all(),
    }
    return render(request, 'shopapp/orders-list.html', context=context)
