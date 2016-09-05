from django.test import TestCase, Client

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from .models import *

import os 

dir_path = os.path.dirname(os.path.realpath(__file__))

class UpdateTest(TestCase):

    def test_simple_request(self):
        c = Client()
        response = c.get('/update/1/LibreOfficeDev/5.3.0.0.alpha0+/test-build/linux-64/en-US/master-daily')
        print(response)

    def test_invalid_api_version(self):
        c = Client()
        response = c.get('/update/1000/LibreOfficeDev/5.3.0.0.alpha0+/test-build/linux-64/en-US/master-daily')
        self.assertEqual(response.status_code, 200)
        content = response.content
        self.assertJSONEqual(content, {'error':'only api version 1 supported right now'})

class UploadTest(TestCase):

    def get_test_file(self, file_name):
        return os.path.join(dir_path, 'data', file_name)

    def setUp(self):
        user = User.objects.create_user('test user')
        self.c = Client()
        self.c.force_login(user)
        self.channel = UpdateChannel.objects.create(name = 'daily-master')

    def test_simple_request(self):
        with open(self.get_test_file('build_config.json'), 'r') as f:
            response = self.c.post('/update/upload/release', {'release_config': f})
        print(response.content)

class ChannelTest(TestCase):

    def test_channel(self):
        c = Client()
        UpdateChannel.objects.create(name='test 1')
        UpdateChannel.objects.create(name='test 2')
        response = c.get('/update/channels')
        self.assertJSONEqual(response.content, ['test 1', 'test 2'])

class PartialTargetTest(TestCase):

    def get_test_file(self, file_name):
        return os.path.join(dir_path, 'data', file_name)

    def setUp(self):
        user = User.objects.create_user('test user')
        self.c = Client()
        self.c.force_login(user)
        self.channel = UpdateChannel.objects.create(name = 'daily-master')

    def test_partial_info(self):
        with open(self.get_test_file('build_config2.json'), 'r') as f:
            response = self.c.post('/update/upload/release', {'release_config': f})
            print(response.content)
            self.assertEqual(200, response.status_code)
        with open(self.get_test_file('build_config.json'), 'r') as f:
            response = self.c.post('/update/upload/release', {'release_config': f})
            self.assertEqual(200, response.status_code)
        with open(self.get_test_file('build_config3.json'), 'r') as f:
            response = self.c.post('/update/upload/release', {'release_config': f})
            self.assertEqual(200, response.status_code)
        response = self.c.get('/update/partial-targets/1/Linux_X86_64/daily-master')
        print(response.content)
