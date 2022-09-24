from rest_framework import permissions
from rest_framework.views import APIView
from .serializers import TenantSerializer
from .models import Tenant, Domain
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from django_tenants.utils import schema_context
from users.models import User
from .task import createcompany

class createCompany(APIView):
    serializer_class = TenantSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = TenantSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            schema_name = serializer.validated_data['schema_name']
            user= request.user
            company_name = serializer.validated_data['company_name']
            password = serializer.validated_data['password']

            data = {
                'schema_name': schema_name,
                'user': user.id,
                'company_name': company_name,
                'password':password
            }
            if createcompany.delay(data):
                return Response({'info': 'Successfully signed-up'}, status=status.HTTP_201_CREATED)
        raise ValidationError({'error': 'something bad happens'})