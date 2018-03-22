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
        self.assertIn('name', resp.json()['global'])

        # Missing distance & time
        data.update({
            'name': 'My nice training',
        })
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('distance_time', resp.json()['global'])

        # Missing note
        data.update({
            'time': '00:15:51',
        })
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('note', resp.json()['global'])

        # Created session
        data.update({
            'note': 3,
        })
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SportSession.objects.count(), 1)


    def test_update_session(self):
        '''
        Update a session
        '''
        # Create a new session
        self.assertEqual(SportSession.objects.count(), 0)
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(
            reverse('api-v2:session-create'),
            {
                'sport': 'running',
                'type': 'training',
                'date': '2020-12-31',
                'name': 'Run boy run',
                'distance': '1000',
                'note': 2,
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        session_id = resp.json()['id']
        self.assertEqual(SportSession.objects.count(), 1)
        session = SportSession.objects.get(pk=session_id)
        self.assertIsNone(session.comment)
        self.assertEqual(session.note, 2)

        # Update session
        session_data = resp.json()
        session_data.update({
            'comment': 'Oooh that was nice',
            'note': 5,
        })
        resp = self.client.put(
            reverse('api-v2:session', args=(session_id, )),
            session_data,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        session = SportSession.objects.get(pk=session_id)
        self.assertIsNotNone(session.comment)
        self.assertEqual(session.comment, 'Oooh that was nice')
        self.assertEqual(session.note, 5)

    def test_delete_session(self):
        '''
        Delete a session
        '''
        # Create a new session
        self.assertEqual(SportSession.objects.count(), 0)
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(
            reverse('api-v2:session-create'),
            {
                'sport': 'cycling',
                'type': 'training',
                'date': '2000-12-31',
                'name': 'Run boy run',
                'distance': '12',
                'comment': 'Long comment... blah',
                'note': 5,
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SportSession.objects.count(), 1)

        # Delete session
        session_id = resp.json()['id']
        url = reverse('api-v2:session', args=(session_id, ))
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SportSession.objects.count(), 0)
