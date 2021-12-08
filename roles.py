import os
import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import threading
from django.db import transaction
from api.users.models import AccessLevel, Role

def add_roles():
    roles = AccessLevel.DICT
    print(roles)
    for acl, role in roles.items():
        print(acl, role)
        role_object = Role.objects.filter(name=role, access_level=acl)
        if role_object.exists():
            print(f'{role} exists')
            continue
        else:
            r = Role(name=role, access_level=acl)
            r.save()
            print(f'{role} newly added.')
    print('All above roles have been added/updated successfully.')


if __name__ == "__main__":
    add_roles()