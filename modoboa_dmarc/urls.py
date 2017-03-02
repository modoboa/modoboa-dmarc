"""DMARC urls."""

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^domains/(?P<pk>\d+)/$", views.DomainReportView.as_view(),
        name="domain_report"),
]
