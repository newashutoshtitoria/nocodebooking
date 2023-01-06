from rest_framework.views import APIView
from django.shortcuts import render
from threading import Thread
from rest_framework import permissions, status
from main.models import *
from main.serializers import UserSignupSerializer
from messages.SendOTP import sendotp
from django.db import connection
from django_tenants.utils import schema_context

class Signup(APIView):
    """
    View for sign up in tenant.
    """
    serializer_class = UserSignupSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            serializer = UserSignupSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                phone_number = serializer.validated_data['phone_number']
                name = serializer.validated_data['name']
                user = User.objects.create_user(phone_number=phone_number, name=name)
                msg_thread = Thread(target=sendotp, args=(user, schema_name))
                msg_thread.start()
                user.save()
                return Response({'info': 'Successfully signed-up', 'user_id': user.id, 'name': name},
                                status=status.HTTP_201_CREATED)
        raise ValidationError({'error': 'Invalid User'})