from django.core.management import BaseCommand

from covid_api.core.cron import update_data


class Command(BaseCommand):
    help = 'Update the COVID-19 data'

    def handle(self, *args, **options):
        update_data()
