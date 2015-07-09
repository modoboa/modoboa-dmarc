"""Import a DMARC aggregated report."""

from optparse import make_option

from django.core.management.base import BaseCommand

from ...lib import import_archive, import_report_from_email


class Command(BaseCommand):

    """Command definition."""

    help = "Import DMARC aggregated reports."

    option_list = BaseCommand.option_list + (
        make_option("--pipe", action="store_true", default=False,
                    help="Import a report from an email given on stdin"),
    )

    def handle(self, *args, **options):
        """Entry point."""
        if options["pipe"]:
            import_report_from_email()
        elif args:
            import_archive(args[0])
