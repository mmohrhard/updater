from django.test import TestCase, Client

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from .models import *

import os 

dir_path = os.path.dirname(os.path.realpath(__file__))

class UpdateTest(TestCase):

    def setUp(self):
        update_channel = UpdateChannel.objects.create(name="master-daily")
        mar_file = MarFile.objects.create(url="www.libreoffice.org", size=100, hash="", hash_function="")
        release = Release.objects.create(name="release", channel=update_channel, product="LibreOfficeDev",
                os="Linux", release_file=mar_file)

    def tearDown(self):
        UpdateChannel.objects.all().delete()
        Release.objects.all().delete()
        MarFile.objects.all().delete()

    def test_simple_request(self):
        c = Client()
        response = c.get('/update/check/1/LibreOfficeDev/test-build/linux-64/master-daily')
        print(response)

    def test_invalid_api_version(self):
        c = Client()
        response = c.get('/update/check/1000/LibreOfficeDev/test-build/linux-64/master-daily')
        self.assertEqual(response.status_code, 200)
        content = response.content
        self.assertJSONEqual(content, {'error':'only api version 1 supported right now'})

    def test_unsupported_build(self):
        c = Client()
        response = c.get('/update/check/1/LibreOfficeDev/test-build/linux-64/master-daily')
        self.assertEqual(response.status_code, 200)
        content = response.content
        self.assertJSONEqual(content, {'response':'Your current build is not supported.'})

    def test_no_supported_update(self):
        c = Client()
        response = c.get('/update/check/1/LibreOfficeDev/release/Linux/master-daily')
        self.assertEqual(response.status_code, 200)
        content = response.content
        self.assertJSONEqual(content, {'response':'There is currently no supported update for your update channel'})

    def test_release_already_uptodate(self):
        pass

class PartialUpdateTest(TestCase):

    def setUp(self):
        update_channel = UpdateChannel.objects.create(name="master-daily")
        mar_file = MarFile.objects.create(url="www.libreoffice.org", size=100, hash="", hash_function="")
        mar_file2 = MarFile.objects.create(url="www.libreoffice.org", size=101, hash="", hash_function="")
        release = Release.objects.create(name="release1", channel=update_channel, product="LibreOfficeDev",
                os="Linux", release_file=mar_file)
        release2 = Release.objects.create(name="release2", channel=update_channel, product="LibreOfficeDev",
                os="Linux", release_file=mar_file2)
        mar_partial_file = MarFile.objects.create(url="www.test.org", size=10, hash="", hash_function="")
        PartialUpdate.objects.create(mar_file=mar_partial_file, old_release=release, new_release=release2)
        update_channel.current_release = release2
        update_channel.save()

    def tearDown(self):
        PartialUpdate.objects.all().delete()
        UpdateChannel.objects.all().delete()
        Release.objects.all().delete()
        MarFile.objects.all().delete()

    def test_partial_update(self):
        c = Client()
        response = c.get('/update/check/1/LibreOfficeDev/release1/Linux/master-daily')
        self.assertEqual(response.status_code, 200)
        content = response.content
        self.assertJSONEqual(content, {"from":"release1","to":"release2","see also":"",
            "languages":{},"update":{"hash":"","hash_function":"","size":10,"url":"www.test.org"}})

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

    def tearDown(self):
        UpdateChannel.objects.all().delete()

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
