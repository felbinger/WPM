from django.apps import AppConfig
from pexpect.pxssh import ExceptionPxssh


class ManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'manager'

    def ready(self):
        from django.conf import settings

        router = settings.VYOS_ROUTER
        try:
            # check connection to vyos when manager app is ready
            router.login()
        except ExceptionPxssh:
            print("Unable to establish connection to router!")
            # TODO exit application: not working
            exit(1)
        finally:
            router.logout()
