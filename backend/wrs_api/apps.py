from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core import management

class AppInitializationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wrs_api'

    def ready(self):
        management.call_command('seed_data')