from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        username = 'root'

        if User.objects.filter(username=username).exists():
            return

        User.objects.create_superuser(username, password='1')
