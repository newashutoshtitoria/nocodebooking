from main.custom_permission import *
from rest_framework import permissions, status
from rest_framework import viewsets
from main.webserializers import CategorySerializer, UserSignupSerializer, OTPSerializer, LoginSerializer, UserAddressSerializer, PackageSerializer
from main.models import Category, UserAddress, PriceTag, Package
from users.models import User, OTP
from django.db import connection
from django_tenants.utils import schema_context
from rest_framework.views import APIView
from messages.SendOTP import sendotp
from threading import Thread
from rest_framework.response import Response
from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import login, logout
from users.token import get_tokens_for_user

class CategoryView(viewsets.ModelViewSet):
    """
    This View is for  of Category.
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (permissions.AllowAny, IstenantuserOrReadOnly)



class PackageView(viewsets.ModelViewSet):
    """
    This View is for  of Packages.
    """
    serializer_class = PackageSerializer
    queryset = Package.objects.all()
    permission_classes = (permissions.AllowAny, IstenantuserOrReadOnly)


class CategoryPackageView(APIView):
    def get(self, request, format=None):
        categories = Category.objects.all()
        data = []
        for category in categories:
            category_data = {
                "category": category.category,
                "packages": []
            }
            for package in category.category_package.all():
                package_data = {
                    "created_on": package.created_on,
                    # Add other fields you want to include here
                }
                category_data["packages"].append(package_data)
            data.append(category_data)
        return Response(data)






class Signup(APIView):
    """
    View for sign up.
    """
    serializer_class = UserSignupSerializer
    permission_classes = (permissions.AllowAny,)

    @atomic
    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            serializer = UserSignupSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                phone_number = serializer.validated_data['phone_number']
                name = serializer.validated_data['name']
                otp_fetching_metching = serializer.validated_data['otp_fetching_metching']
                user = User.objects.create_user(phone_number=phone_number, name=name)

                msg_thread = Thread(target=sendotp, args=(user,schema_name,otp_fetching_metching))
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
            otp_fetching_metching = None
            msg_thread = Thread(target=sendotp, args=(user, schema_name,otp_fetching_metching))
            msg_thread.start()
            return Response({'info': 'Resent OTP', 'user_id': user.id, 'name': user.name},
                            status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    User for logging in.
    """
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            phone_number = serializer.validated_data['phone_number']
            otp_fetching_metching = serializer.validated_data['otp_fetching_metching']
            user = User.objects.get(phone_number=phone_number)
            msg_thread = Thread(target=sendotp, args=(user, schema_name,otp_fetching_metching))
            msg_thread.start()
            return Response({'info': 'successful! Otp sent', 'user_id': user.id, 'name': user.name},
                            status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    logout view.Only authenticated user can access this url(by default)
    """
    def get(self, request, *args, **kwargs):
        logout(request)
        return Response({'message':'successfully logged out'},
                        status=status.HTTP_200_OK)


class ProfileView(APIView):
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



class UserAddressView(viewsets.ModelViewSet):
    """
    View for handling User's address i.e CRUD.
    """
    serializer_class = UserAddressSerializer
    permission_classes = (permissions.IsAuthenticated, IsUser)
    queryset = UserAddress.objects.all()

    def list(self, request):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            queryset = UserAddress.objects.filter(user=request.user.id)
            serializer = UserAddressSerializer(queryset, many=True)
            return Response(serializer.data)

    def perform_create(self, serializer):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            user = self.request.user
            count = UserAddress.objects.filter(user=user).count()
            if count == 4:
                raise ValidationError({'error': "Not Allowed"})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user)
