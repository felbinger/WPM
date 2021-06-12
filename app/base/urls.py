from django.urls import path
from os import environ

from .views import index

urlpatterns = [
    path('', index, name='index'),
]

# register oauth routes
if environ.get('OAUTH_URL', False):
    from .views import oauth, oauth_redirect

    urlpatterns.append(path('oauth/', oauth, name='oauth'))
    urlpatterns.append(path('oauth/redirect', oauth_redirect, name='oauth_redirect'))
