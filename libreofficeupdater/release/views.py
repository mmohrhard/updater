from django.shortcuts import render

from django import forms

from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from .models import *

import json
import logging

logger = logging.getLogger(__name__)

class UploadRelease(forms.Form):
    release_config = forms.FileField()

def update_check(request, api_version, product, version, build_id, os, locale, channel):
    print(api_version)
    if int(api_version) != 1:
        return JsonResponse({'error' : 'only api version 1 supported right now'})

    matched_releases = Release.objects.filter(os = os, channel__name = channel).order_by('-added')
    if matched_releases.count() == 0:
        return JsonResponse({'response': 'no update available'})

    print(matched_releases)
    print(version)
    print(build_id)
    print(locale)

    return JsonResponse({'foo':'bar'})

def handle_file(file_dict):
    url = file_dict['url']
    size = int(file_dict['size'])
    hash = file_dict['hash']
    hash_function = file_dict['hashFunction']
    return MarFile.objects.create(url=url, size=size, hash=hash, hash_function=hash_function)

@login_required
@csrf_exempt
def upload_release(request):
    if request.method == 'GET':
        form = UploadRelease()
        return HttpResponse(form.as_ul())
    elif request.method != 'POST':
        return HttpResponseNotAllowed('Only GET or POST allowed')

    form = UploadRelease(request.POST, request.FILES)

    if not form.is_valid():
        logger.error("form is invalid with error: " + str(form.errors))
        print(str(form.errors))
        return HttpResponseBadRequest()

    file = request.FILES['release_config']
    data = json.load(file)
    update_channel_str = data['updateChannel']
    platform_str = data['platform']
    product_name_str = data['productName']
    build_number_str = data['buildNumber']

    update_channel = get_object_or_404(UpdateChannel, name=update_channel_str)

    new_release = Release.objects.create(name = build_number_str, channel = update_channel,
            product = product_name_str, os = platform_str, release_file = handle_file(data['complete']))
    for language in data['languages']:
        LanguageFile.objects.create(language=language['lang'], release=new_release, mar_file=handle_file(language['complete']))

    return JsonResponse({})

def get_channels(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed('Only GET allowed')

    channels = UpdateChannel.objects.values('name')
    channel_names = [channel['name'] for channel in channels]
    return JsonResponse(channel_names, safe=False)
