"""AppConfig for dmarc."""

from django.apps import AppConfig


class DmarcConfig(AppConfig):

    """App configuration."""

    name = "modoboa_dmarc"
    verbose_name = "Modoboa DMARC tools"

    def ready(self):
        from . import handlers
