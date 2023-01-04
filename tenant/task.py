from celery import shared_task
from time import sleep
from .models import Tenant, Domain
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from django_tenants.utils import schema_context
from users.models import User

@shared_task
def sleepy(duration):
    sleep(duration)
    return None

@shared_task
def createcompany(data):
    schema_name = data['schema_name']
    user = User.objects.get(id=data['user'])
    company_name = data['company_name']

    try:
        check_tenant = user.tenant_user
    except:
        check_tenant = None

    if check_tenant is None:
        tenant = Tenant.objects.create(schema_name=schema_name, user=user, company_name=company_name)
        tenant.is_active = True
        tenant.save()
        domain = Domain()
        domain.domain = str(schema_name) + '.bookeve.in'
        domain.tenant = tenant
        domain.is_primary = True
        domain.save()


        # with schema_context(schema_name):
        #     User.objects.create_superuser(phone_number=user.phone_number, name=user.name, password=password)

        return True


#no schadule just for testing purpose
def createcompanynocelery(data):
    schema_name = data['schema_name']
    user = User.objects.get(id=data['user'])
    company_name = data['company_name']

    try:
        check_tenant = user.tenant_user
    except:
        check_tenant = None

    if check_tenant is None:
        tenant = Tenant.objects.create(schema_name=schema_name, user=user, company_name=company_name)
        tenant.is_active = True
        tenant.save()
        domain = Domain()
        domain.domain = str(schema_name) + '.bookeve.in'
        domain.tenant = tenant
        domain.is_primary = True
        domain.save()

        #
        # with schema_context(schema_name):
        #     User.objects.create_superuser(phone_number=user.phone_number, name=user.name, password=password)

        return True
    return False