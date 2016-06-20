"""Custom template tags."""

import datetime

from dateutil import relativedelta

from django import template
from django.utils.safestring import mark_safe

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
