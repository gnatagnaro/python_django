from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Product, Order
from .forms import ProductForm, OrderForm, GroupForm

# Create your views here.


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        :param request:
        :return:
        """
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {'time_running': default_timer(),
                   'products': products,
                   }
        return render(request, 'shopapp/shop-index.html', context=context)


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


class ProductDetailsView(DetailView):
    template_name = 'shopapp/product-details.html'
    # model = Product
    context_object_name = 'product'
    queryset = (
        Product.objects.filter(archived=False)
    )

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

# def products_list(request: HttpRequest) -> HttpResponse:
#     context = {
#         'products': Product.objects.all(),
#     }
#     return render(request, 'shopapp/products-list.html', context=context)


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm  # аналогично: fields = 'name', 'price', 'description', 'discount'
    success_url = reverse_lazy('shopapp:products_list')

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


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('shopapp:products_list')
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs={'pk': self.object.pk}
        )


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(ListView):
    # template_name = 'shopapp/order_list.html'
    # model = Order
    # context_object = 'orders'
    queryset = (
        Order.objects.select_related('user').prefetch_related('products')
    )

# def orders_list(request: HttpRequest) -> HttpResponse:
#     context = {
#         'orders': Order.objects.select_related('user').prefetch_related('products').all(),
#     }
#     return render(request, 'shopapp/order_list.html', context=context)


class OrdersDetailView(DetailView):
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