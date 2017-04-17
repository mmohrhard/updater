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

def get_update_file(update_file):
    data = { 'url': update_file.url,
            'hash': update_file.hash,
            'size': update_file.size,
            'hash_function': update_file.hash_function}

    return data

def update_check(request, api_version, product, build_id, os, locale, channel):
    if int(api_version) != 1:
        return JsonResponse({'error' : 'only api version 1 supported right now'})

    update_channel = get_object_or_404(UpdateChannel, name = channel)

    # first find the corresponding release that the user currently has
    current_user_release = Release.objects.filter(os = os, channel = update_channel, name = build_id, product=product)
    if current_user_release.count() == 0:
        return JsonResponse({'response': 'Your current build is not supported.'})

    current_user_release = current_user_release[0]

    current_update_channel_release = update_channel.current_release
    if current_update_channel_release is None:
        return JsonResponse({'response': 'There is currently no supported update for your update channel'})

    if current_update_channel_release == current_user_release:
        return JsonResponse({'response': 'Your release is already updated.'})

    print(current_user_release)
    print(locale)

    data = { 'from': '*', # full mar works for any previous build
            'see also': current_update_channel_release.see_also,
            'update': get_update_file(current_update_channel_release.release_file),
            'languages': {}}

    return JsonResponse(data)

def partial_targets(request, api_version, channel, os):
    if int(api_version) != 1:
        return JsonResponse({'error' : 'only api version 1 supported right now'})

    matched_releases = Release.objects.filter(os = os, channel__name = channel).order_by('-added')
    data = []
    for release in matched_releases[:3]:
        languages = LanguageFile.objects.filter(release = release)
        languages_return = [{'lang': language.language, 'file': get_update_file(language.mar_file)} for language in languages]
        partial = {'complete': get_update_file(release.release_file),
                'languages': languages_return}

        data.append(partial)
    return JsonResponse(data, safe = False)

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

def get_releases(request, channel):
    if request.method != 'GET':
        return HttpResponseNotAllowed('Only GET allowed')

    update_channel = get_object_or_404(UpdateChannel, name=channel)
    releases = Release.objects.filter(channel=update_channel).values('name')
    release_names = [release['name'] for release in releases]
    return JsonResponse(release_names, safe=False)
