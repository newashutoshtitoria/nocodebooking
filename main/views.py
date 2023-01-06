from rest_framework.views import APIView
from django.shortcuts import render
from threading import Thread
from rest_framework import permissions, status
from main.models import *
from main.serializers import UserSignupSerializer, OTPSerializer
from messages.SendOTP import sendotp
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from users.models import OTP
from users.token import get_tokens_for_user
from django.db import connection
from django_tenants.utils import schema_context

User = get_user_model()

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
                otp_fetching_metching = request.data['otp_fetching_metching']
                msg_thread = Thread(target=sendotp, args=(user, schema_name, otp_fetching_metching))
                msg_thread.start()
                user.save()
                return Response({'info': 'Successfully signed-up', 'user_id': user.id, 'name': name},
                                status=status.HTTP_201_CREATED)
        raise ValidationError({'error': 'Invalid User'})


class Activate(APIView):
    """
    Activate verifies the stored otp and the otp entered by user.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = OTPSerializer

    def post(self, request, user_id,*args,**kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            serializer = OTPSerializer(data=request.data)
            code_otp = request.data['otp']
            try:
                otp = OTP.objects.get(receiver=user_id)
            except(TypeError, ValueError, OverflowError, OTP.DoesNotExist):
                otp = None
            try:
                receiver = User.objects.get(id=user_id)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                receiver = None
            if otp is None or receiver is None:
                raise ValidationError({'error': 'you are not a valid user'})
            elif timezone.now() - otp.sent_on >= timedelta(days=0, hours=0, minutes=1, seconds=0):
                # otp.delete()
                raise ValidationError({'error': 'OTP expired!'})

            if str(otp.otp) == str(code_otp):
                if receiver.active is False:
                    serializer.is_valid(raise_exception=True)
                    receiver.active = True
                    receiver.save()
                otp.delete()
                refresh, access = get_tokens_for_user(receiver, schema_name)
                return Response({'message': 'Successful', 'refresh': refresh, 'access': access})
            else:
                raise ValidationError({'error': 'Invalid OTP'})