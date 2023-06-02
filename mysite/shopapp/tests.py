from string import ascii_letters
from random import choices

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from mysite import settings
from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='user', password='password')
        permission = Permission.objects.get(codename='add_product')
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.product_name = ''.join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_product_create(self):
        response = self.client.post(
            reverse('shopapp:product_create'),
            {
                'name': self.product_name,
                'price': 5000.99,
                'description': 'A good car',
                'discount': 10,

            }
        )

        self.assertRedirects(response, reverse('shopapp:products_list'))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create(username='kk', password='kk')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.product = Product.objects.create(
            name='new',
            description='the best',
            price=100,
            discount=10,
            created_by=self.user,
        )

    def tearDown(self) -> None:
        self.product.delete()

    def test_get_product(self):
        response = self.client.get(reverse('shopapp:product_details', kwargs={"pk": self.product.pk}))
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(reverse('shopapp:product_details', kwargs={"pk": self.product.pk}))
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='1', password='password')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    fixtures = [
        'products-fixture.json',
    ]

    def test_products(self):
        response = self.client.get(reverse('shopapp:products_list'))
        # self.assertQuerySetEqual(
        #     qs=Product.objects.filter(archived=False).all(),
        #     values=[(p.pk for p in response.context['products'])],
        #     transform=lambda p: p.pk,
        # )
        self.assertTemplateUsed(response, 'shopapp/products-list.html')


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='test', password='test')
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        # self.client.force_login(self.user)
        self.client.login(**self.credentials)

    def test_orders_view(self):
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertContains(response, 'Orders')

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # super().setUpClass()
        cls.user = User.objects.create_user(username='test', password='test')
        permission = Permission.objects.get(codename='view_order')
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        # super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.order = Order.objects.create(delivery_address='Test Address', promocode='TESTCODE', user=self.user)

    def tearDown(self) -> None:
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(reverse('shopapp:order_details', args=[self.order.pk]))
        self.assertEqual(response.status_code, 200)

        # Проверяем, что адрес заказа присутствует в теле ответа
        self.assertContains(response, self.order.delivery_address)

        # Проверяем, что промокод присутствует в теле ответа
        self.assertContains(response, self.order.promocode)

        # Проверяем, что заказ присутствует в контексте ответа
        self.assertEqual(response.context['order'].pk, self.order.pk)
        # self.assertIn(self.order.delivery_address, response.content.decode())
        # self.assertIn(self.order.promocode, response.content.decode())


class OrderCreateViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='test', password='test')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.product = Product.objects.create(
            name='new',
            description='the best',
            price=100,
            discount=10,
            created_by=self.user,
        )

    def tearDown(self) -> None:
        self.product.delete()

    def test_order_create(self):
        response = self.client.post(
            reverse('shopapp:order_create'),
            {
                'delivery_address': 'street',
                'promocode': 'code',
                'user': self.user,
                'products': self.product,
            }
        )
        self.assertEqual(response.status_code, 200)
        # self.assertRedirects(response, reverse('shopapp:orders_list'))


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'users-fixture.json',
        'products-fixture.json',
        'auth-group-fixture.json',
        'auth-permission-fixture',
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse('shopapp:products-export'))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'price': str(product.price),
                'archived': product.archived,
            }
            for product in products
        ]
        product_data = response.json()
        self.assertEqual(product_data['products'], expected_data)


class OrdersExportViewTestCase(TestCase):
    fixtures = [
        'users-fixture.json',
        'products-fixture.json',
        'orders-fixture.json',
        'auth-group-fixture.json',
        'auth-permission-fixture',
        'auth-user-fixture',
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='newuser', password='del123d54')
        cls.user.is_staff = True
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_get_orders_view(self):
        response = self.client.get(reverse('shopapp:orders-export'))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user_id,
                'products_id': [product.id for product in order.products.all()]
            }
            for order in orders
        ]
        order_data = response.json()
        self.assertEqual(order_data['orders'], expected_data)
