from rest_framework.views import APIView
from rest_framework import permissions, status
from .serializers import *
from rest_framework.response import Response
from .permissions import *
from rest_framework import status, filters
from rest_framework.exceptions import ValidationError
from threading import Thread
from .permissions import *
from django.utils import timezone
from datetime import timedelta
from .token import get_tokens_for_user
from messages.SendOTP import sendotp, phonechangeotp
from threading import Thread
from django_tenants.utils import remove_www
from django.db import connection
from django_tenants.utils import schema_context
from django.contrib.auth import login, logout


class Signup(APIView):
    """
    View for sign up.
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
                msg_thread = Thread(target=sendotp,args=(user,schema_name))
                msg_thread.start()
                user.save()
                return Response({'info': 'Successfully signed-up', 'user_id': user.id, 'name': name}, status=status.HTTP_201_CREATED)
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
                    receiver.phone_validated = True
                    receiver.save()
                otp.delete()
                refresh, access = get_tokens_for_user(receiver)
                return Response({'message': 'Successful', 'refresh': refresh, 'access': access})
            else:
                raise ValidationError({'error': 'Invalid OTP'})



class ResendOtp(APIView):
    """
    views for resend the otp.
    """
    serializer_class = OTPSerializer
    permission_classes = (permissions.AllowAny,)

    def get(self, request, user_id, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            try:
                user = User.objects.get(id=user_id)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            if user is None:
                raise ValidationError({'error': 'Not a valid user!'})
            msg_thread = Thread(target=sendotp, args=(user,schema_name))
            msg_thread.start()
            return Response({'info': 'Resent OTP', 'user_id': user.id, 'name': user.name},
                            status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    logout view.Only authenticated user can access this url(by default)
    """
    def get(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            logout(request)
            return Response({'message': 'successfully logged out'},
                            status=status.HTTP_200_OK)


class LoginView(APIView):
    """
    Used for logging in.
    """
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            phone_number = serializer.validated_data['phone_number']
            user = User.objects.get(phone_number=phone_number)
            msg_thread = Thread(target=sendotp,args=(user,schema_name))
            msg_thread.start()
            return Response({'info': 'successful! Otp sent', 'user_id': user.id, 'name': user.name}, status=status.HTTP_201_CREATED)


class userdetail(APIView):
    """
    Profile View of User.
    """
    serializer_class = UserSignupSerializer
    permission_classes = (permissions.AllowAny,permissions.IsAuthenticated)

    def get(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            try:
                user_id = self.request.user.id
                user = User.objects.get(id=user_id)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            if user:
                serializer = UserSignupSerializer(data={"phone_number": user.phone_number, "name": user.name})
                serializer.is_valid()
                return Response(serializer.data)
            raise ValidationError({'error': 'Not a valid user'})


class changephonenumber(APIView):
    serializer_class = phonenumberchangeserializer
    permission_classes = (permissions.IsAuthenticated, IsadminOrIsOwner )

    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            serializer = phonenumberchangeserializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                phone_number = serializer.validated_data['phone_number']
                try:
                    request_phonenumber = requestednewphonenumber.objects.get(user=request.user)
                except(TypeError, ValueError, OverflowError, requestednewphonenumber.DoesNotExist):
                    request_phonenumber = None
                if request_phonenumber or request_phonenumber is not None:
                    request_phonenumber.delete()
                requestednewphonenumber.objects.create(user = request.user, phone_number=phone_number)
                msg_thread = Thread(target=phonechangeotp, args=(request.user, schema_name, phone_number))
                msg_thread.start()
                return Response({'info': 'Successfully signed-up', 'user_id': request.user.id, 'name': request.user.name},
                                status=status.HTTP_201_CREATED)


class newphone_validate(APIView):
    """
    Activate verifies the stored otp and the otp entered by user.
    """
    permission_classes = (permissions.IsAuthenticated, IsadminOrIsOwner )
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
                raise ValidationError({'error': 'OTP expired!'})

            if str(otp.otp) == str(code_otp):
                serializer.is_valid(raise_exception=True)
                try:
                    request_phonenumber = requestednewphonenumber.objects.get(user=receiver)
                except(TypeError, ValueError, OverflowError, requestednewphonenumber.DoesNotExist):
                    request_phonenumber = None

                if request_phonenumber or request_phonenumber is not None:
                    new_phone_number = request_phonenumber.phone_number
                    receiver.phone_number = new_phone_number
                    receiver.active = True
                    receiver.phone_validated = True
                    receiver.save()
                    request_phonenumber.delete()

                otp.delete()
                refresh, access = get_tokens_for_user(receiver)
                return Response({'message': 'Successful', 'refresh': refresh, 'access': access})
            else:
                raise ValidationError({'error': 'Invalid OTP'})




