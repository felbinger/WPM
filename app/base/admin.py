from os import environ
from django.contrib import admin

# remove oauth provider from admin
if environ.get('OAUTH_URL', False):
    from oauth2_provider.models import AccessToken, Application, IDToken, Grant, RefreshToken

    admin.site.unregister(AccessToken)
    admin.site.unregister(Application)
    admin.site.unregister(IDToken)
    admin.site.unregister(Grant)
    admin.site.unregister(RefreshToken)
