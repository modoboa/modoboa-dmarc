"""DMARC tools for Modoboa."""

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy, ugettext as _

from modoboa.core.extensions import ModoExtension, exts_pool
from modoboa.lib import events, parameters

from . import __version__


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
        from .app_settings import ParametersForm

        parameters.register(ParametersForm, "DMARC")


exts_pool.register_extension(DmarcExtension)


@events.observe("GetDomainActions")
def extra_domain_actions(user, domain):
    """Return a menu to show the DMARC report."""
    return [{
        "name": "dmarc_report",
        "url": reverse("modoboa_dmarc:domain_report", args=[domain.pk]),
        "title": _("Show DMARC report for {}").format(domain.name),
        "img": "fa fa-pie-chart"
    }]
