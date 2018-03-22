from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import Athlete
from sport.models import SportSession


class SportTests(APITestCase):
    '''
    Test the sport API
    '''
    fixtures = [
        'sport/data/sports.json',
    ]

    def setUp(self):
        # Create a user

        self.user = Athlete.objects.create(email='test@test.com', username='crasher')

    def test_new_session(self):
        '''
        Create a new session
        '''
        url = reverse('api-v2:session-create')
        self.assertEqual(SportSession.objects.count(), 0)

        # No auth
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # Auth
        self.client.force_authenticate(user=self.user)

        # Missing date
        data = {
            'sport': 'running',
            'type': 'training',
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date', resp.json().keys())

        # Missing name
        data.update({
            'date': '2018-01-01',
        })
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', resp.json()['errors'])

        # Missing distance & time
        data.update({
            'name': 'My nice training',
        })
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('distance_time', resp.json()['errors'])

        # Missing note
        data.update({
            'time': '00:15:51',
        })
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('note', resp.json()['errors'])

        # Created session
        data.update({
            'note': 3,
        })
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SportSession.objects.count(), 1)
