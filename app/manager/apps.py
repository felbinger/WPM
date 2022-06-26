from django.apps import AppConfig
from pexpect.pxssh import ExceptionPxssh


class ManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'manager'
