from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest
from django.shortcuts import redirect, render
import requests
from django.urls import reverse


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


def oauth(request: HttpRequest) -> HttpResponse:
    return redirect(settings.OAUTH_URL)


def oauth_redirect(request: HttpRequest) -> HttpResponse:
    if 'code' not in request.GET:
        return HttpResponseBadRequest()

    auth_resp = requests.post("https://discord.com/api/oauth2/token", data={
        "client_id": settings.OAUTH_CLIENT_ID,
        "client_secret": settings.OAUTH_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": request.GET.get('code'),
        "redirect_uri": f"{settings.SCHEMA}://{settings.PUBLIC_URL}{reverse('base:oauth_redirect')}",
        "scope": "identify"
    }, headers={
        'Content-Type': 'application/x-www-form-urlencoded'
    })

    if not auth_resp.ok:
        return HttpResponseBadRequest()

    identity_resp = requests.get('https://discord.com/api/v8/users/@me', headers={
        'Authorization': f'{auth_resp.json().get("token_type")} {auth_resp.json().get("access_token")}'
    })
    if not identity_resp.ok:
        return HttpResponseBadRequest()

    user, _ = User.objects.get_or_create(username=identity_resp.json().get('id'))

    login(request, user, backend="oauth2_provider.backends.OAuth2Backend")

    return redirect(settings.LOGIN_REDIRECT_URL)
