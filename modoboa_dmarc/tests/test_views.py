"""Views tests."""

from django.urls import reverse

from modoboa.admin import factories as admin_factories
from modoboa.core import models as core_models
from modoboa.lib.tests import ModoTestCase

from . import mixins


class DMARCViewsTestCase(mixins.CallCommandMixin, ModoTestCase):
    """Views test cases."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        super(DMARCViewsTestCase, cls).setUpTestData()
        cls.domain = admin_factories.DomainFactory(name="ngyn.org")

    def test_domainlist_view(self):
        """Test domain list view."""
        self.import_reports()
        user = core_models.User.objects.get(username="admin")
        self.client.force_login(user)
        url = reverse("admin:_domain_list")
        response = self.ajax_get(url)
        url = reverse("modoboa_dmarc:domain_report", args=[self.domain.pk])
        self.assertIn(url, response["rows"])

    def test_domainreport_view(self):
        """Test domain report view."""
        self.import_reports()
        user = core_models.User.objects.get(username="admin")
        self.client.force_login(user)
        url = reverse("modoboa_dmarc:domain_report", args=[self.domain.pk])
        response = self.client.get("{}?period=2015-26".format(url))
        self.assertContains(response, "'Failed', 100.0")

    def test_domainreport_view_week0(self):
        """Test domain report view."""
        self.import_reports()
        user = core_models.User.objects.get(username="admin")
        self.client.force_login(user)
        url = reverse("modoboa_dmarc:domain_report", args=[self.domain.pk])
        response = self.client.get("{}?period=2019-0".format(url))
        self.assertContains(response, "Dec. 31, 2018")

    def test_domainreport_view_week52(self):
        """Test domain report view."""
        self.import_reports()
        user = core_models.User.objects.get(username="admin")
        self.client.force_login(user)
        url = reverse("modoboa_dmarc:domain_report", args=[self.domain.pk])
        response = self.client.get("{}?period=2018-52".format(url))
        self.assertContains(response, "Dec. 30, 2018")

