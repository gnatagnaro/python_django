from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from shopapp.models import Product, Order, ProductImage
from .admin_mixins import ExportAsCSVMixin

# Register your models here.


class OrderInline(admin.TabularInline):
    model = Product.orders.through


class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.action(description='Archive products')
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description='Unarchive products')
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [
        mark_archived,
        mark_unarchived,
        'export_csv',
    ]
    inlines = [
        OrderInline,
        ProductInline,
    ]
    # list_display = 'pk', 'name', 'description', 'price', 'discount'
    readonly_fields = ('created_at',)
    list_display = 'pk', 'name', 'description_short', 'price', 'discount', 'created_at', 'archived',
    list_display_links = 'pk', 'name'
    ordering = ('pk',)
    search_fields = 'name', 'description', 'created_at'
    list_filter = ['archived']
    fieldsets = [
        ('Main' or None, {
            'fields': ('name', 'description'),
        }),
        ('Price Options', {
            'fields': ('price', 'discount'),
            'classes': ('wide', 'collapse'),
        }),
        ('Extra Options', {
            'fields': ('archived',),
            'classes': ('collapse',),
            'description': 'Field "archived" is for soft delete',
        }),
        ('Date', {
            'fields': ('created_at',),
            'classes': ('wide',),
        }),
        ('Images', {
            'fields': ('preview',),
        }),
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + '...'
# admin.site.register(Product, ProductAdmin)


# class ProductInline(admin.TabularInline):
class ProductInline(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        ProductInline,
    ]
    readonly_fields = ('created_at',)
    list_display = ('pk', 'delivery_address', 'promocode', 'created_at', 'user_verbose', 'receipt',)
    list_display_links = ('pk', 'delivery_address', 'receipt',)
    ordering = ('pk',)
    search_fields = ('pk', 'delivery_address', 'promocode', 'created_at', 'user_verbose',)
    fieldsets = [
        ('Main', {
           'fields': ('delivery_address', 'promocode', 'receipt'),
           'classes': ('wide', 'collapse',)
        }),
        ('User Options', {
           'fields': ('user', ),
           'classes': ('wide', 'collapse'),
        }),
        ('Date', {
            'fields': ('created_at',),
            'classes': ('wide',),
        }),
    ]

    def get_queryset(self, request):
        return Order.objects.select_related('user').prefetch_related('products')

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username
