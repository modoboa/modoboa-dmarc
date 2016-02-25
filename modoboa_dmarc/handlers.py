"""Django signal handlers for modoboa_dmarc."""

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.dispatch import receiver

from modoboa.admin.signals import extra_domain_actions

from . import models


@receiver(extra_domain_actions)
def dmarc_domain_actions(sender, **kwargs):
    """Return a link to access domain report."""
    domain = kwargs.get("domain")
    if not domain:
        return
    if not models.Record.objects.filter(header_from=domain).exists():
        return
    return [{
        "name": "dmarc_report",
        "url": reverse("modoboa_dmarc:domain_report", args=[domain.pk]),
        "title": _("Show DMARC report for {}").format(domain.name),
        "img": "fa fa-pie-chart"
    }]
