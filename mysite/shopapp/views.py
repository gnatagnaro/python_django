"""
В этом модуле лежат различные наборы представлений.

View интернет-магазина: по товарам, заказам и т.д.
"""

from timeit import default_timer

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from docutils.nodes import description
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Order, ProductImage
from .forms import ProductForm, OrderForm, GroupForm
from .serializers import ProductSerializer, OrderSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse


@extend_schema(description='Product views CRUD')
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD для сущностей товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = [
        'name',
        'description',
    ]
    ordering_fields = [
        'name',
        'price',
        'discount',
    ]

    filterset_fields = [
        'name',
        'description',
        'price',
        'discount',
        'archived',
    ]

    @extend_schema(
        summary='Get one product by ID',
        description='Retrieves **product**, returns 404 if not found',
        responses={
            200: ProductSerializer,
            400: OpenApiResponse(description='Empty response, product by id not found'),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = [
        'delivery_address',
        'promocode',
        'created_at',
    ]
    ordering_fields = [
        'delivery_address',
        'promocode',
        'created_at',
        'user',
        'products',
    ]

    filterset_fields = [
        'delivery_address',
        'promocode',
        'created_at',
        'user',
        'products',
    ]


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            'time_running': default_timer(),
            'products': products,
            'items': 5,
        }
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            'form': GroupForm(),
            'groups': Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        # return redirect(reverse('shopapp:groups_list'))
        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = 'shopapp/product-details.html'
    # model = Product
    context_object_name = 'product'
    queryset = Product.objects.prefetch_related('images')
    # Product.objects.filter(archived=False),

    # def get(self, request: HttpRequest, pk: int) -> HttpResponse:
    #     # product = Product.objects.get(pk=pk)
    #     product = get_object_or_404(Product, pk=pk)
    #     context = {
    #         'product': product,
    #     }
    #     return render(request, 'shopapp/product-details.html', context=context)


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    # model = Product
    context_object_name = 'products'
    queryset = (
        Product.objects.filter(archived=False)
    )

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['products'] = Product.objects.all()
    #     return context


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'shopapp.add_product'

    # def test_func(self):
    #     return self.request.user.is_superuser
    model = Product
    form_class = ProductForm  # аналогично: fields = 'name', 'price', 'description', 'discount'
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    # В задании просят прописывать методы гет и пост, но зачем, если в классе CreateView все происходит под капотом.
    # def get(self, request: HttpRequest) -> HttpResponse:
    #     form = ProductForm()
    #     context = {
    #         'form': form,
    #     }
    #     return render(request, 'shopapp/product_form.html', context=context)
    #
    # def post(self, request: HttpRequest) -> HttpResponse:
    #     form = ProductForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         # url = reverse('shopapp:products_list')
    #     return redirect(request.path)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return self.request.user.is_superuser or (
                user.has_perm('shopapp.change_product') and product.created_by == user)

    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('shopapp:products_list')
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs={'pk': self.object.pk}
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist('images'):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    # template_name = 'shopapp/order_list.html'
    # model = Order
    # context_object = 'orders'
    queryset = (
        Order.objects.select_related('user').prefetch_related('products')
    )


class OrdersDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'shopapp.view_order'
    queryset = (
        Order.objects.select_related('user').prefetch_related('products')
    )


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('shopapp:orders_list')


class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('shopapp:orders_list')
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'shopapp:order_details',
            kwargs={'pk': self.object.pk}
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('shopapp:orders_list')


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by('pk').all()
        products_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'price': product.price,
                'archived': product.archived,
            }
            for product in products
        ]
        return JsonResponse({'products': products_data})


class OrdersDataExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by('pk').all()
        orders_data = [
            {
                'pk': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user_id,
                'products_id': [product.id for product in order.products.all()]
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})

# def create_order(request: HttpRequest) -> HttpResponse:
#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             form.save()
#             url = reverse('shopapp:orders_list')
#             return redirect(url)
#     else:
#         form = OrderForm()
#     context = {
#         'form': form,
#     }
#     return render(request, 'shopapp/order_form.html', context=context)


# def create_product(request: HttpRequest) -> HttpResponse:
#     if request.method == 'POST':
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             # name = form.cleaned_data['name']
#             # price = form.cleaned_data['price']
#             # discount = form.cleaned_data['discount']
#             # Product.objects.create(name=name, price=price, discount=discount)
#             # Product.objects.create(**form.cleaned_data)
#             form.save()
#             url = reverse('shopapp:products_list')
#             return redirect(url)
#     else:
#         form = ProductForm()
#     context = {
#         'form': form,
#     }
#     return render(request, 'shopapp/product_form.html', context=context)

# def orders_list(request: HttpRequest) -> HttpResponse:
#     context = {
#         'orders': Order.objects.select_related('user').prefetch_related('products').all(),
#     }
#     return render(request, 'shopapp/order_list.html', context=context)

# def products_list(request: HttpRequest) -> HttpResponse:
#     context = {
#         'products': Product.objects.all(),
#     }
#     return render(request, 'shopapp/products-list.html', context=context)


#
# def shop_index(request: HttpRequest) -> HttpResponse:
#     """
#     :param request:
#     :return:
#     """
#     products = [
#         ('Laptop', 1999),
#         ('Desktop', 2999),
#         ('Smartphone', 999),
#     ]
#     context = {'time_running': default_timer(),
#                'products': products,
#                }
#     return render(request, 'shopapp/shop-index.html', context=context)

# def groups_list(request: HttpRequest) -> HttpResponse:
#     """
#
#     :param request:
#     :return:
#     """
#     context = {
#         'groups': Group.objects.prefetch_related('permissions').all(),
#     }
#     return render(request, 'shopapp/groups-list.html', context=context)
