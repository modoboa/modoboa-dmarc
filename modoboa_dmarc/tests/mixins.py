"""Test mixins."""

import os
import sys

import six

from django.core.management import call_command


class CallCommandMixin(object):
    """A mixin to provide command execution shortcuts."""

    def setUp(self):
        """Replace stdin"""
        super(CallCommandMixin, self).setUp()
        self.stdin = sys.stdin

    def tearDown(self):
        sys.stdin = self.stdin

    def import_report(self, path):
        """Import test report from file."""
        with open(path) as fp:
            buf = six.StringIO(fp.read())
        sys.stdin = buf
        call_command("import_aggregated_report", "--pipe")

    def import_reports(self, folder="reports"):
        """Import reports from folder."""
        path = os.path.join(os.path.dirname(__file__), folder)
        for f in os.listdir(path):
            fpath = os.path.join(path, f)
            if f.startswith(".") or not os.path.isfile(fpath):
                continue
            self.import_report(fpath)
