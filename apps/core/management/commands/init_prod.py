from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Init prod: create admin superuser and seed demo data if empty (for Render without shell)"

    def handle(self, *args, **options):
        User = get_user_model()
        # Create superuser admin / admin@gmail.com / admin
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(username="admin", email="admin@gmail.com", password="admin")
            self.stdout.write(self.style.SUCCESS("Created superuser admin / admin@gmail.com"))
        else:
            # ensure email/password correct and is superuser/staff
            user = User.objects.get(username="admin")
            updated = False
            if user.email != "admin@gmail.com":
                user.email = "admin@gmail.com"
                updated = True
            if not user.is_superuser or not user.is_staff:
                user.is_superuser = True
                user.is_staff = True
                updated = True
            # reset password to admin if needed (check using check_password)
            if not user.check_password("admin"):
                user.set_password("admin")
                updated = True
            if updated:
                user.save()
                self.stdout.write(self.style.SUCCESS("Updated superuser admin"))
            else:
                self.stdout.write("Superuser admin already exists")

        # Seed data only if empty to avoid duplicates on every restart
        from apps.mechanics.models import Mechanic

        if Mechanic.objects.count() == 0:
            self.stdout.write("No mechanics found — seeding demo data...")
            call_command("seed_data")
            self.stdout.write(self.style.SUCCESS("Seeded demo data"))
        else:
            self.stdout.write(f"Skipping seed — {Mechanic.objects.count()} mechanics already present")
