# travel/management/commands/create_staff_user.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crear usuario staff para operaciones'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True)
        parser.add_argument('--email', type=str, required=True)
        parser.add_argument('--password', type=str, required=True)

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username=options['username'],
            defaults={
                'email': options['email'],
                'is_staff': True,
                'is_superuser': False
            }
        )
        
        if created:
            user.set_password(options['password'])
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Usuario staff {options["username"]} creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Usuario {options["username"]} ya existe')
            )