"""Custom template tags."""

import datetime

from dateutil import relativedelta
from collections import OrderedDict

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.simple_tag
def next_period(period):
    """Return next period."""
    current = datetime.datetime.strptime("{}-1".format(period), "%Y-%W-%w")
    current += relativedelta.relativedelta(weeks=1)
    parts = current.isocalendar()
    return mark_safe("{}-{}".format(parts[0], parts[1]))


@register.simple_tag
def previous_period(period):
    """Return previous period."""
    current = datetime.datetime.strptime("{}-1".format(period), "%Y-%W-%w")
    current += relativedelta.relativedelta(weeks=-1)
    parts = current.isocalendar()
    return mark_safe("{}-{}".format(parts[0], parts[1]))


@register.filter
def domain_sorted_items(domain_dict):
    """Return a list of tuples ordered alphabetically by domain names."""
    if isinstance(domain_dict, dict):
        sorted_domain_dict = OrderedDict(
            sorted(domain_dict.items(), key=lambda t: t[0]))
        unresolved_label = _("Not resolved")
        unresolved = sorted_domain_dict.pop(unresolved_label, None)
        if unresolved:
            sorted_domain_dict[unresolved_label] = unresolved
        return sorted_domain_dict.items()

    raise ValueError("domain_dict is not a dict")
