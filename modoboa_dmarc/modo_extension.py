"""DMARC tools for Modoboa."""

from django.utils.translation import ugettext_lazy

from modoboa.core.extensions import ModoExtension, exts_pool
from modoboa.parameters import tools as param_tools

from . import __version__
from . import forms


class DmarcExtension(ModoExtension):
    """Extension registration."""

    name = "modoboa_dmarc"
    label = ugettext_lazy("DMARC tools")
    version = __version__
    description = ugettext_lazy(
        "A set of tools to ease DMARC integration"
    )
    url = "dmarc"

    def load(self):
        """Extension loading."""
        param_tools.registry.add("global", forms.ParametersForm, "DMARC")


exts_pool.register_extension(DmarcExtension)
