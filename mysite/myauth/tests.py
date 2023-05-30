from django.test import TestCase
from django.urls import reverse
# import json


class GetCookieViewTestCase(TestCase):
    def test_get_cookie_view(self):
        response = self.client.get(reverse('myauth:cookie-get'))
        self.assertContains(response, 'Cookie value')


class FooBarViewTestCase(TestCase):
    def test_foo_bar_view(self):
        response = self.client.get(reverse('myauth:foo-bar'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'application/json',)
        # expected_data = {'foo': 'bar', 'spam': 'eggs'}
        # received_data = json.loads(response.content)
        # self.assertEqual(received_data, expected_data)
        self.assertJSONEqual(response.content, {'foo': 'bar', 'spam': 'eggs'})
