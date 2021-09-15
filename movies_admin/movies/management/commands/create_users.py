from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        root_username = 'root'
        admin_username = 'admin'

        if not User.objects.filter(username=root_username).exists():
            User.objects.create_superuser(root_username, password='1')

        if not User.objects.filter(username=admin_username).exists():
            User.objects.create_user(admin_username, password='1', is_staff=True)
