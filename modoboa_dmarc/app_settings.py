# coding: utf-8

"""Online settings."""

from django.utils.translation import ugettext_lazy as _

from modoboa.lib.form_utils import (
    SeparatorField, YesNoField,
)
from modoboa.lib.parameters import AdminParametersForm


class ParametersForm(AdminParametersForm):

    """Extension settings."""

    app = "modoboa_dmarc"

    qsettings_sep = SeparatorField(label=_("DNS settings"))

    enable_rlookups = YesNoField(
        label=_("Enable reverse lookups"),
        initial="no",
        help_text=_(
            "Enable reverse DNS lookups (reports will be longer to display)"
        )
    )
