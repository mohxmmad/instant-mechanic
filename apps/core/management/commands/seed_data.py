import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.mechanics.models import Mechanic
from apps.service_requests.models import ServiceRequest
from apps.accounts.models import User

MECHANICS = [
    ("Rahul Sharma", "Gurgaon", ["engine repair", "oil change"], 4.5, True),
    ("Amit Verma", "Delhi", ["brake service", "tire replacement"], 4.2, True),
    ("Suresh Kumar", "Noida", ["ac repair", "electrical"], 4.8, False),
    ("Priya Singh", "Gurgaon", ["denting painting", "car wash"], 4.0, True),
    ("Vikash Patel", "Faridabad", ["general service", "diagnostics"], 3.9, True),
    ("Anil Yadav", "Delhi", ["battery replacement", "towing"], 4.6, False),
    ("Deepak Mehta", "Gurgaon", ["engine repair", "general service"], 4.3, True),
    ("Neha Gupta", "Noida", ["oil change", "brake service"], 4.7, True),
    ("Rohan Kapoor", "Delhi", ["ac repair", "electrical", "diagnostics"], 3.8, True),
    ("Sunita Rao", "Faridabad", ["car wash", "denting painting"], 4.1, True),
]

SERVICES = ["engine repair", "oil change", "brake service", "tire replacement", "battery replacement", "ac repair", "denting painting", "general service", "electrical", "towing", "car wash", "diagnostics"]

CUSTOMERS = [
    ("Arjun Mehra", "MH01AB1234"),
    ("Kavita Desai", "DL08CA5678"),
    ("Rohit Singh", "HR26DK9999"),
    ("Sneha Patel", "UP16AB0001"),
    ("Manish Kumar", "GJ01AB1234"),
    ("Pooja Sharma", "RJ14CA1111"),
    ("Vijay Joshi", "KA05MH4321"),
    ("Anjali Verma", "TN09AB9876"),
]

class Command(BaseCommand):
    help = "Seed realistic demo data for mechanics and service requests"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Clear existing data before seeding")

    def handle(self, *args, **options):
        if options["clear"]:
            ServiceRequest.objects.all().delete()
            Mechanic.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing mechanics and service requests"))

        # Ensure demo user
        if not User.objects.filter(username="demo").exists():
            User.objects.create_user(username="demo", email="demo@example.com", password="demo12345")
            self.stdout.write(self.style.SUCCESS("Created demo user: demo / demo12345"))

        mechanics = []
        phones = [f"9{random.randint(100000000, 999999999)}" for _ in range(len(MECHANICS))]
        for idx, (name, location, services, rating, is_open) in enumerate(MECHANICS):
            m, created = Mechanic.objects.get_or_create(
                name=name,
                location=location,
                defaults={
                    "phone": phones[idx],
                    "rating": rating + random.uniform(-0.2, 0.2),
                    "is_open": is_open,
                    "services": services,
                }
            )
            if created:
                # clamp rating
                m.rating = max(0, min(5, round(float(m.rating), 2)))
                m.save()
            mechanics.append(m)

        self.stdout.write(self.style.SUCCESS(f"Ensured {len(mechanics)} mechanics"))

        # Create service requests
        statuses = [c[0] for c in ServiceRequest.Status.choices]
        problems = [
            "Engine making noise",
            "Brake pads worn out",
            "AC not cooling",
            "Battery dead",
            "Tire puncture",
            "General servicing required",
            "Electrical issue with lights",
            "Car wash and polishing",
        ]

        created_count = 0
        for i in range(20):
            cust_name, vehicle = random.choice(CUSTOMERS)
            mechanic = random.choice(mechanics)
            # Vary dates: last 30 days
            days_ago = random.randint(0, 30)
            status = random.choice(statuses)

            sr = ServiceRequest.objects.create(
                customer_name=cust_name,
                customer_phone=f"9{random.randint(100000000, 999999999)}",
                vehicle_number=vehicle,
                mechanic=mechanic,
                service=random.choice(SERVICES),
                problem_description=random.choice(problems),
                status=status,
            )
            # Hack created_at to spread dates
            sr.created_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            sr.updated_at = sr.created_at
            sr.save(update_fields=["created_at", "updated_at"])
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} service requests"))
        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
