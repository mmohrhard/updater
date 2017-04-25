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

def find_partial_update(old_release, new_release):
    partial_update = PartialUpdate.objects.get(old_release=old_release, new_release=new_release)
    return partial_update

def update_check(request, api_version, product, build_id, os, channel):
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

    # try to find a partial update from the old to the new release
    try:
        partial_update = find_partial_update(current_user_release, current_update_channel_release)
        if partial_update:
            languages = {}
            data = {'from': current_user_release.name,
                    'to': current_update_channel_release.name,
                    'see also': current_update_channel_release.see_also,
                    'update': get_update_file(partial_update.mar_file),
                    'languages': languages}
            return JsonResponse(data)
    except:
        pass

    # fall back to a full mar

    # collect the language pack update info
    language_objects = LanguageFile.objects.filter(release=current_update_channel_release)
    languages = {}
    for language_object in language_objects:
        languages[language_object.language] = get_update_file(language_object.mar_file)

    data = { 'from': '*', # full mar works for any previous build
            'to': current_update_channel_release.name,
            'see also': current_update_channel_release.see_also,
            'update': get_update_file(current_update_channel_release.release_file),
            'languages': languages}

    return JsonResponse(data)

def partial_targets(request, api_version, channel, os):
    if int(api_version) != 1:
        return JsonResponse({'error' : 'only api version 1 supported right now'})

    update_channel = get_object_or_404(UpdateChannel, name = channel)
    matched_releases = Release.objects.filter(os = os, channel = update_channel).order_by('-added')
    data = {'updates':[]}
    print(matched_releases.count())
    print(os)
    print(channel)
    num_updates = update_channel.num_partial_updates
    for release in matched_releases[:num_updates]:
        language_objects = LanguageFile.objects.filter(release = release)
        languages = {}
        for language_object in language_objects:
            languages[language_object.language] = get_update_file(language_object.mar_file)
        partial = {'update': get_update_file(release.release_file),
                'build': release.name,
                'languages': languages}

        data['updates'].append(partial)
    return JsonResponse(data)

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

    update_channel.current_release = new_release
    update_channel.save()

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
