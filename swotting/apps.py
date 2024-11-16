from django.apps import AppConfig

class SwottingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'swotting'

    def ready(self):
        try:
            import swotting.tasks  # This ensures tasks are loaded
        except ImportError:
            pass
