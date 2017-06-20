# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.core.exceptions import MiddlewareNotUsed

redisAvailable = True

try:
    import redis
except ImportError:
    redisAvailable = False
    pass

class HitCountingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        if not redisAvailable:
            raise MiddlewareNotUsed()

        self.r = redis.Redis(
                host='127.0.0.1',
                port=6379)
        try:
            self.r.ping()
        except redis.ConnectionError:
            raise MiddlewareNotUsed()

    def __call__(self, request):
        self.r.incr(request.path_info)

        response = self.get_response(request)

        return response

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
