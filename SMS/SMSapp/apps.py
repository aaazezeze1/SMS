from django.apps import AppConfig

class SmsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SMSapp'

    def ready(self):
        import SMSapp.signals
