from django.core.management.base import BaseCommand
from authentication.models import FoAUserConnection, User


class Command(BaseCommand):

    def handle(self, *args, **options):

        for user in User.objects.all():
            FoAUserConnection.objects.create(user=user, foa=user.field_of_activity)