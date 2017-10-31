"""Management command tests."""

from modoboa.admin import factories as admin_factories
from modoboa.lib.tests import ModoTestCase

from . import mixins
from .. import models


class ManagementCommandTestCase(mixins.CallCommandMixin, ModoTestCase):
    """Test management command."""

    @classmethod
    def setUpTestData(cls):
        super(ManagementCommandTestCase, cls).setUpTestData()
        cls.domain = admin_factories.DomainFactory(name="ngyn.org")

    def test_import_from_archive(self):
        """Import report from archive."""
        self.import_reports()
        self.assertTrue(self.domain.record_set.exists())
        self.assertTrue(
            models.Reporter.objects.filter(
                org_name="FastMail Pty Ltd").exists())
