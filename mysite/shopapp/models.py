from django.contrib.auth.models import User
from django.db import models


def product_preview_directory_path(instance: 'Product', filename: str) -> str:
    return 'products/product_{pk}/preview/{filename}'.format(
        pk=instance.pk,
        filename=filename
    )


class Product(models.Model):
    class Meta:
        ordering = ['name', 'price']
    name = models.CharField(max_length=100)
    description = models.TextField(null=False, blank=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    archived = models.BooleanField(default=False)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)

    # @property
    # def description_short(self) -> str:
    #     if len(self.description) < 48:
    #         return self.description
    #     return self.description[:48] + '...'

    def __str__(self) -> str:
        return f'Product (pk={self.pk}, name={self.name!r})'


def product_images_directory_path(instance: 'ProductImage', filename: str) -> str:
    return 'products/product_{pk}/preview/{filename}'.format(
        pk=instance.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, null=True, blank=True)


class Order(models.Model):
    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # one-to-many
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    # many-to-many
    products = models.ManyToManyField(Product, related_name='orders')

    receipt = models.FileField(null=True, upload_to='orders/receipts/')

    def __str__(self) -> str:
        return f'Order (pk={self.pk})'
