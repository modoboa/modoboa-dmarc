"""Internal library."""

import datetime
import email
import fileinput
from lxml import objectify
from StringIO import StringIO
import zipfile

from django.db import transaction

from modoboa_admin import models as admin_models

from . import models

ZIP_CONTENT_TYPES = [
    "application/x-zip-compressed",
    "application/x-zip",
    "application/zip"
]


def import_record(xml_node, report):
    """Import a record."""
    record = models.Record(report=report)
    record.source_ip = xml_node.row.source_ip
    record.count = int(xml_node.row.count)

    record.disposition = xml_node.row.policy_evaluated.disposition
    record.dkim_result = xml_node.row.policy_evaluated.dkim
    record.spf_result = xml_node.row.policy_evaluated.spf
    if hasattr(xml_node.row.policy_evaluated, "reason"):
        record.reason_type = xml_node.row.policy_evaluated.reason.type
        record.reason_comment = xml_node.row.policy_evaluated.reason.comment

    record.header_from = admin_models.Domain.objects.filter(
        name=xml_node.identifiers.header_from).first()
    if record.header_from is None:
        print "Invalid record found (domain not local"
        return None

    record.save()
    for rtype in ["spf", "dkim"]:
        if not hasattr(xml_node.auth_results, rtype):
            continue
        rnode = getattr(xml_node.auth_results, rtype)
        models.Result.objects.create(
            record=record, type=rtype, domain=rnode.domain,
            result=rnode.result)


@transaction.atomic
def import_report(content):
    """Import an aggregated report."""
    feedback = objectify.fromstring(content)
    print "Importing new report received from {}".format(
        feedback.report_metadata.org_name)
    reporter, created = models.Reporter.objects.get_or_create(
        org_name=feedback.report_metadata.org_name,
        email=feedback.report_metadata.email
    )
    qs = models.Report.objects.filter(
        reporter=reporter, report_id=feedback.report_metadata.report_id)
    if qs.exists():
        print "Report already imported."""
        return
    report = models.Report(reporter=reporter)

    report.report_id = feedback.report_metadata.report_id
    report.start_date = datetime.datetime.fromtimestamp(
        feedback.report_metadata.date_range.begin)
    report.end_date = datetime.datetime.fromtimestamp(
        feedback.report_metadata.date_range.end)

    for attr in ["domain", "adkim", "aspf", "p", "sp", "pct"]:
        try:
            setattr(
                report, "policy_{}".format(attr),
                getattr(feedback.policy_published, attr)
            )
        except AttributeError:
            pass
    report.save()
    for record in feedback.record:
        import_record(record, report)


def import_archive(archive):
    """Import reports contained inside a zip archive (file pointer)."""
    with zipfile.ZipFile(archive, "r") as zfile:
        for fname in zfile.namelist():
            import_report(zfile.read(fname))


def import_report_from_email():
    """Parse a report from stdin."""
    content = StringIO()
    for line in fileinput.input([]):
        content.write(line)
    content.seek(0)

    if not content:
        return
    msg = email.message_from_file(content)
    for part in msg.walk():
        if part.get_content_type() not in ZIP_CONTENT_TYPES:
            continue
        fpo = StringIO(part.get_payload(decode=True))
        import_archive(fpo)
        fpo.close()
