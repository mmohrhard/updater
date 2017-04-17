# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.conf.urls import url

from . import views

urlpatterns = [
        url(r'partial-targets/(?P<api_version>.+)/(?P<os>.+)/(?P<channel>.+)$', views.partial_targets),
        url(r'check/(?P<api_version>.+)/(?P<product>.+)/(?P<build_id>.+)/(?P<os>.+)/(?P<locale>.+)/(?P<channel>.+)$', views.update_check, name='update_check'),
        url(r'upload/release$', views.upload_release, name='upload_release'),
        url(r'channels$', views.get_channels, name='channels'),
        url(r'releases/(?P<channel>.+)$', views.get_releases, name='releases')
        ]



# vim:set shiftwidth=4 softtabstop=4 expandtab: */
