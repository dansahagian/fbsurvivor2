from django.core.management.base import BaseCommand

from fbsurvivor.core.utils.reminders import send_reminders


class Command(BaseCommand):
    help = "Send reminders to the league."

    def handle(self, *args, **options):
        send_reminders()
