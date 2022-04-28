"""Internal library."""

import datetime
import email
import fileinput
import getpass
import imaplib
import zipfile
import gzip
import sys

from defusedxml.ElementTree import fromstring
import pytz.exceptions
import six
import magic

from django.db import transaction
from django.utils.encoding import smart_text
from django.utils import timezone

from modoboa.admin import models as admin_models

from . import constants
from . import models

ZIP_CONTENT_TYPES = [
    "application/x-zip-compressed",
    "application/x-zip",
    "application/zip",
    "application/gzip",
    "application/octet-stream",
    "text/xml",
]

FILE_TYPES = [
    "text/plain",
    "text/xml",
]


def import_record(xml_node, report):
    """Import a record."""
    record = models.Record(report=report)
    row = xml_node.find("row")
    record.source_ip = row.find("source_ip").text
    record.count = int(row.find("count").text)

    policy_evaluated = row.find("policy_evaluated")
    record.disposition = policy_evaluated.find("disposition").text
    record.dkim_result = policy_evaluated.find("dkim").text
    record.spf_result = policy_evaluated.find("spf").text
    reason = policy_evaluated.find("reason")
    if reason:
        record.reason_type = smart_text(reason.find("type").text)[:14]
        if record.reason_type not in constants.ALLOWED_REASON_TYPES:
            record.reason_type = "other"
        comment = reason.find("comment").text or ""
        record.reason_comment = comment

    identifiers = xml_node.find("identifiers")
    header_from = identifiers.find("header_from").text.split(".")
    domain = None
    while len(header_from) >= 2:
        domain = admin_models.Domain.objects.filter(
            name=".".join(header_from)).first()
        if domain is not None:
            record.header_from = domain
            break
        header_from = header_from[1:]
    if domain is None:
        print("Invalid record found (domain not local)")
        return None

    record.save()
    auth_results = xml_node.find("auth_results")
    for rtype in ["spf", "dkim"]:
        rnode = auth_results.find(rtype)
        if not rnode:
            continue
        models.Result.objects.create(
            record=record, type=rtype, domain=rnode.find("domain").text,
            result=rnode.find("result").text)


@transaction.atomic
def import_report(content):
    """Import an aggregated report."""
    root = fromstring(content, forbid_dtd=True)
    metadata = root.find("report_metadata")
    print(
        "Importing report {} received from {}".format(
            metadata.find("report_id").text,
            metadata.find("org_name").text)
    )
    reporter, created = models.Reporter.objects.get_or_create(
        email=metadata.find("email").text,
        defaults={"org_name": metadata.find("org_name").text}
    )
    qs = models.Report.objects.filter(
        reporter=reporter, report_id=metadata.find("report_id").text)
    if qs.exists():
        print("Report already imported.")
        return
    report = models.Report(reporter=reporter)

    report.report_id = metadata.find("report_id").text
    date_range = metadata.find("date_range")
    report.start_date = timezone.make_aware(
        datetime.datetime.fromtimestamp(int(date_range.find("begin").text))
    )
    report.end_date = timezone.make_aware(
        datetime.datetime.fromtimestamp(int(date_range.find("end").text))
    )

    policy_published = root.find("policy_published")
    for attr in ["domain", "adkim", "aspf", "p", "sp", "pct"]:
        node = policy_published.find(attr)
        if node is None or not node.text:
            print(f"Report skipped because of malformed data (empty {attr})")
            return
        value = setattr(report, "policy_{}".format(attr), node.text)
    try:
        report.save()
    except (pytz.exceptions.AmbiguousTimeError):
        print("Report skipped because of invalid date.")
        return
    for record in root.findall("record"):
        import_record(record, report)


def import_archive(archive, content_type=None):
    """Import reports contained inside (file pointer)
    - a zip archive,
    - a gzip file,
    - a xml file.
    """
    if content_type == "text/xml":
        import_report(archive.read())
    elif content_type in ["application/gzip", "application/octet-stream"]:
        with gzip.GzipFile(mode="r", fileobj=archive) as zfile:
            import_report(zfile.read())
    else:
        with zipfile.ZipFile(archive, "r") as zfile:
            for fname in zfile.namelist():
                import_report(zfile.read(fname))


def import_report_from_email(content):
    """Import a report from an email."""
    if isinstance(content, six.string_types):
        msg = email.message_from_string(content)
    elif isinstance(content, six.binary_type):
        msg = email.message_from_bytes(content)
    else:
        msg = email.message_from_file(content)
    err = False
    for part in msg.walk():
        if part.get_content_type() not in ZIP_CONTENT_TYPES:
            continue
        try:
            fpo = six.BytesIO(part.get_payload(decode=True))
            # Try to get the actual file type of the buffer
            # required to make sure we are dealing with an XML file
            file_type = magic.Magic(uncompress=True, mime=True).from_buffer(fpo.read(2048))
            fpo.seek(0)
            if file_type in FILE_TYPES:
                import_archive(fpo, content_type=part.get_content_type())
        except (OSError, IOError):
            print('Error: the attachment does not match the mimetype')
            err = True
        else:
            fpo.close()
    if err:
        # Return EX_DATAERR code <data format error> available
        # at sysexits.h file
        # (see http://www.postfix.org/pipe.8.html)
        sys.exit(65)


def import_report_from_stdin():
    """Parse a report from stdin."""
    content = six.StringIO()
    for line in fileinput.input([]):
        content.write(line)
    content.seek(0)

    if not content:
        return
    import_report_from_email(content)


def import_from_imap(options):
    """Import reports from an IMAP mailbox."""
    obj = imaplib.IMAP4_SSL if options["ssl"] else imaplib.IMAP4
    conn = obj(options["host"])
    username = input("Username: ")
    password = getpass.getpass(prompt="Password: ")
    conn.login(username, password)
    conn.select(options["mailbox"])
    type, msg_ids = conn.search(None, "ALL")
    for msg_id in msg_ids[0].split():
        typ, content = conn.fetch(msg_id, "(RFC822)")
        for response_part in content:
            if isinstance(response_part, tuple):
                import_report_from_email(response_part[1])
    conn.close()
