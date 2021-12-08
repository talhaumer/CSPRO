from django.conf import settings
from django.core.management import BaseCommand
from django.db import transaction
from django.contrib.auth.models import Group, Permission
from api.zone.models import  Countries, Zone
from api.users.models import User, UserInfo, Role


def superuser():
    try:
        name = "SuperUser"
        is_active = True
        email = settings.SUPER_USER or "csprosuperadmin@yopmail.com"
        is_approved = True
        is_active = True
        is_staff = True
        role = 'super_admin'
        password = "Pass1234@"
        is_superuser = True
        with transaction.atomic():
            user_obj = {"name":name,
                        "email":email,
                        "is_active":is_active,
                        'is_approved':is_approved,
                        'role':Role.objects.get(code = role),
                        "is_superuser" : is_superuser,
                        'country':Countries.objects.get(id = 1)
                        }
            user = User.objects.create(**user_obj)
            user.set_password(password)
            user.save()
            user_info = {
                "user":user,
                'zone':Zone.objects.get(code= 'world'),
                "mail_notification":True
            }
            UserInfo.objects.create(**user_info)
            print(f'Email : {email}')
            print(f'Password : {password}')
            print('User is created')
    except Exception as e:
        print(e)
        print(f"User is not created exception:{e}")


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            superuser()
        except Exception as e:
            print(e)