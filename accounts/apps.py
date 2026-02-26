from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Akkauntlar'

    def ready(self):
        # Signal'larni import qilamiz — app tayyor bo'lganda
        import accounts.signals  # noqa