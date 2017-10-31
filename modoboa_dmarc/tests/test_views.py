"""Views tests."""

from django.core.urlresolvers import reverse

from modoboa.admin import factories as admin_factories
from modoboa.core import models as core_models
from modoboa.lib.tests import ModoTestCase

from .. import models
from . import mixins


class DMARCViewsTestCase(mixins.CallCommandMixin, ModoTestCase):
    """Views test cases."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        super(DMARCViewsTestCase, cls).setUpTestData()
        cls.domain = admin_factories.DomainFactory(name="ngyn.org")

    def test_domainreport_view(self):
        """Test domain report view."""
        self.import_reports()
        user = core_models.User.objects.get(username="admin")
        self.client.force_login(user)
        url = reverse("modoboa_dmarc:domain_report", args=[self.domain.pk])
        response = self.client.get("{}?period=2015-26".format(url))
        self.assertContains(response, "'Failed', 100.0")
