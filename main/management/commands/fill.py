import json

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from MedProject import settings
from main.models import SiteContent


def load_from_json(file_name):
    with open(f'{settings.BASE_DIR}/json/{file_name}.json', 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


class Command(BaseCommand):

    def handle(self, *args, **options):

        for content in load_from_json('site_content'):
            try:
                SiteContent.objects.create(name=content['name'], content=content['content'])
            except IntegrityError:
                pass