from rest_framework import permissions
from rest_framework.views import APIView
from .serializers import TenantSerializer, DomainSerializer
from .models import Tenant, Domain
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from django_tenants.utils import schema_context
from users.models import User
from .task import createcompany
from django.db import connection
from django_tenants.utils import schema_context

class createCompany(APIView):
    serializer_class = TenantSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        if schema_name == 'public':
            serializer = TenantSerializer(data=request.data)

            if serializer.is_valid(raise_exception=True):
                schema_name = serializer.validated_data['schema_name']
                user = request.user
                company_name = serializer.validated_data['company_name']
                password = serializer.validated_data['password']

                data = {
                    'schema_name': schema_name,
                    'user': user.id,
                    'company_name': company_name,
                    'password': password
                }
                if createcompany.delay(data):
                    return Response({'info': 'Successfully signed-up'}, status=status.HTTP_201_CREATED)
        raise ValidationError({'error': 'something bad happens, you can create a site'})




#do this in userapp instead
class domainChange(APIView):
    serializer_class = DomainSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            if request.user.admin:
                domain = Domain.objects.get(tenant=request.user.tenant_user)

                print(domain.domain, ">>>>>>>>>>>>>>>>>>>>", request.user.name, request.user.tenant_user.schema_name, request.user.tenant_user)
