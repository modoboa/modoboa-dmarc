"""DMARC urls."""

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    "modoboa_dmarc.views",

    url(r"^domains/(?P<pk>\d+)/$", views.DomainReportView.as_view(),
        name="domain_report"),

)
