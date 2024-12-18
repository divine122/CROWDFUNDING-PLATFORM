from django.apps import AppConfig


class DonationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'donations'

    
    def ready(self) -> None:
       import donations.signals
