from rest_framework import permissions
from rest_framework.views import APIView
from .serializers import TenantSerializer, TenantSubscriptionSerializer
from .models import *
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from django_tenants.utils import schema_context
from users.models import User
from .task import createcompany, createcompanynocelery
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

                #without celery
                if createcompanynocelery(data):
                    return Response({'info': 'Successfully signed-up'}, status=status.HTTP_201_CREATED)

                #with celery
                # if createcompany.delay(data):
                #     return Response({'info': 'Successfully signed-up'}, status=status.HTTP_201_CREATED)
        raise ValidationError({'error': 'something bad happens, you can create a site'})


class tenatsubscription(APIView):
    serializer_class = TenantSubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        if schema_name == 'public':
            serializer = TenantSubscriptionSerializer(data=request.data)

            if serializer.is_valid(raise_exception=True):
                date_billing_start = serializer.validated_data['date_billing_start']
                date_billing_end = serializer.validated_data['date_billing_end']
                date_billing_last = serializer.validated_data['date_billing_last']
                date_billing_next = serializer.validated_data['date_billing_next']
                date_billing_start = serializer.validated_data['date_billing_start']
                date_billing_start = serializer.validated_data['date_billing_start']
                user = request.user
                #get schema name
                try:
                    check_user_teanant = user.tenant_user
                    print(check_user_teanant, ">>>>>>>>>>>>>>>>")
                except:
                    pass

                return Response({'ashu': 'asu'})