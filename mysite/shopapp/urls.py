"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ShopIndexView,
    GroupsListView,
    ProductsListView,
    ProductCreateView,
    ProductsDataExportView,
    ProductDetailsView,
    ProductUpdateView,
    ProductDeleteView,
    OrdersListView,
    OrdersDetailView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    OrdersDataExportView,
    ProductViewSet,
    OrderViewSet,
)

app_name = 'shopapp'

routers = DefaultRouter()
routers.register('products', ProductViewSet)
routers.register('orders', OrderViewSet)


urlpatterns = [
    path('api/', include(routers.urls), name='api'),

    path('', ShopIndexView.as_view(), name='index'),

    path('groups/', GroupsListView.as_view(), name='groups_list'),

    path('products/', ProductsListView.as_view(), name='products_list'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/export/', ProductsDataExportView.as_view(), name='products-export'),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name='product_details'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/archive/', ProductDeleteView.as_view(), name='product_delete'),

    path('orders/', OrdersListView.as_view(), name='orders_list'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/export/', OrdersDataExportView.as_view(), name='orders-export'),
    path('orders/<int:pk>/', OrdersDetailView.as_view(), name='order_details'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
]
