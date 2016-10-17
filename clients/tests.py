from django.test import TestCase, Client
from clients.models import Client as Cl
from django.db import transaction, IntegrityError


class RegTest(TestCase):
    def setUp(self):
        pass

    def test(self):
        client = Client()
        url = 'http://127.0.0.1:8000/client/api/registration/'

        # check get request
        response = client.get(url)
        self.assertEqual(response.status_code, 405)

        # check empty request
        response = client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('errors' in response.data)

        # check empty fields
        response = client.post(url, {
            'first_name': '',
            'last_name': '',
            'email': '',
            'password1': '',
            'password2': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('errors' in response.data)

        # check passwords comparing
        response = client.post(url, {
            'first_name': 'Igor',
            'last_name': 'Vusyk',
            'email': 'site@site.com',
            'password1': '12345',
            'password2': '11111',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('errors' in response.data)
        self.assertTrue('password2' in response.data['errors'])

        # check email format validation
        response = client.post(url, {
            'first_name': 'Igor',
            'last_name': 'Vusyk',
            'email': 'bAddd email',
            'password1': '11111',
            'password2': '11111',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('errors' in response.data)
        self.assertTrue('email' in response.data['errors'])

        # check email unique
        response = client.post(url, {
            'first_name': 'Igor',
            'last_name': 'Vusyk',
            'email': 'user@site.com',
            'password1': '11111',
            'password2': '11111',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('success' in response.data)

        response = client.post(url, {
            'first_name': 'Igor',
            'last_name': 'Vusyk',
            'email': 'user@site.com',
            'password1': '11111',
            'password2': '11111',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('errors' in response.data)
        self.assertTrue('email' in response.data['errors'])

        count = Cl.objects.filter(email__exact='user@site.com').count()
        self.assertEqual(1, count)

