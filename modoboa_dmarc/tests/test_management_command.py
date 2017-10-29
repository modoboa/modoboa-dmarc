"""Management command tests."""

import os
import sys

from six import StringIO

from django.core.management import call_command

from modoboa.admin import factories as admin_factories
from modoboa.lib.tests import ModoTestCase

from .. import models


class ManagementCommandTestCase(ModoTestCase):
    """Test management command."""

    @classmethod
    def setUpTestData(cls):
        super(ManagementCommandTestCase, cls).setUpTestData()
        cls.domain = admin_factories.DomainFactory(name="ngyn.org")

    def setUp(self):
        """Replace stdin"""
        super(ManagementCommandTestCase, self).setUp()
        self.stdin = sys.stdin

    def tearDown(self):
        sys.stdin = self.stdin

    def test_import_from_archive(self):
        """Import report from archive."""
        path = os.path.join(os.path.dirname(__file__), "reports")
        for f in os.listdir(path):
            fpath = os.path.join(path, f)
            if f.startswith(".") or not os.path.isfile(fpath):
                continue
            with open(fpath) as fp:
                buf = StringIO(fp.read())
            sys.stdin = buf
            call_command("import_aggregated_report", "--pipe")
        self.assertTrue(self.domain.record_set.exists())
        self.assertTrue(
            models.Reporter.objects.filter(
                org_name="FastMail Pty Ltd").exists())
