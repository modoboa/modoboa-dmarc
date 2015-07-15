"""Import a DMARC aggregated report."""

from optparse import make_option

from django.core.management.base import BaseCommand

from ... import lib


class Command(BaseCommand):

    """Command definition."""

    help = "Import DMARC aggregated reports."

    option_list = BaseCommand.option_list + (
        make_option("--pipe", action="store_true", default=False,
                    help="Import a report from an email given on stdin"),
        make_option("--imap", action="store_true", default=False,
                    help="Import a report from an IMAP mailbox"),
        make_option("--host", default="localhost",
                    help="IMAP host"),
        make_option("--ssl", action="store_true", default=False,
                    help="Connect using SSL"),
        make_option("--mailbox", default="INBOX",
                    help="IMAP mailbox to import reports from"),
    )

    def handle(self, *args, **options):
        """Entry point."""
        if options.get("pipe"):
            lib.import_report_from_stdin()
        elif options.get("imap"):
            lib.import_from_imap(options)
        elif args:
            lib.import_archive(args[0])
        else:
            print "Nothing to do."
