from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

class Command(BaseCommand):
    help = "Creates a default superuser"

    def handle(self, *args, **kwargs):
        email = "admin@example.com"
        password = "adminpassword"

        # Check if the user with the given email already exists
        if not User.objects.filter(email=email).exists():
            # Create the superuser if it doesn't exist
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superuser with email '{email}' created successfully."))
        else:
            self.stdout.write(self.style.WARNING(f"Superuser with email '{email}' already exists."))
