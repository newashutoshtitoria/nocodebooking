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
from tenant.models import Domain
from core.settings import domain_choices



class tenantuserSignup(APIView):
    """
    View for Tenant sign up.
    """
    serializer_class = TenantUserSignupSerializer
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context('public'):
            try:
                check_user = User.objects.get(phone_number=request.data['phone_number'])
            except:
                check_user = None

            if check_user or check_user is not None:
                try:
                    check_user_teanant = check_user.tenant_user

                    return Response({'info': 'Already a User', 'user_id': check_user.id, 'name': check_user.name, 'tenant': check_user_teanant.schema_name},
                                    status=status.HTTP_201_CREATED)
                except:
                    check_user.delete()

            serializer = TenantUserSignupSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                phone_number = serializer.validated_data['phone_number']
                name = serializer.validated_data['name']
                password = serializer.validated_data['password']

                user = User.objects.create_public_user(phone_number=phone_number, name=name, password=password)
                otp_fetching_metching = request.data['otp_fetching_metching']
                msg_thread = Thread(target=sendotp, args=(user, schema_name,otp_fetching_metching ))
                msg_thread.start()
                user.save()
                return Response({'info': 'Successfully signed-up', 'user_id': user.id, 'name': name},
                                status=status.HTTP_201_CREATED)

        raise ValidationError({'error': 'Something Bad Happend'})



class Activate(APIView):
    """
    Activate verifies the stored otp and the otp entered by user.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = OTPSerializer

    def post(self, request, user_id,*args,**kwargs):
        schema_name = connection.schema_name
        with schema_context('public'):
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
                refresh, access = get_tokens_for_user(receiver, schema_name)
                return Response({'message': 'Successful', 'access': access, 'refresh': refresh})
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
        with schema_context('public'):
            try:
                user = User.objects.get(id=user_id)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            if user is None:
                raise ValidationError({'error': 'Not a valid user!'})
            otp_fetching_metching = ''
            msg_thread = Thread(target=sendotp, args=(user,schema_name, otp_fetching_metching))
            msg_thread.start()
            return Response({'info': 'Resent OTP', 'user_id': user.id, 'name': user.name},
                            status=status.HTTP_201_CREATED)



class AdminLoginView(APIView):
    """
    Login for admin.
    """
    serializer_class = AdminLoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        with schema_context('public'):
            try:
                check_user = User.objects.get(phone_number=request.data['phone_number'])
            except:
                check_user = None
            if check_user or check_user is not None:
                try:
                    check_user_teanant = check_user.tenant_user
                except:
                    check_user_teanant = None

                if check_user_teanant or check_user_teanant is not None:
                    if check_user_teanant.is_active:
                        schema_name = check_user_teanant.schema_name
                        with schema_context(schema_name):
                            serializer = AdminLoginSerializer(data=request.data)
                            serializer.is_valid(raise_exception=True)
                            phone_number = serializer.validated_data['phone_number']
                            password = serializer.validated_data['password']
                            user = User.objects.get(phone_number=phone_number)
                            if user.check_password(password):
                                refresh, access = get_tokens_for_user(user, schema_name)
                                with schema_context('public'):
                                    refresh_public, access_public = get_tokens_for_user(check_user, 'public')
                                    return Response({'message': 'Successful', 'tenant': check_user_teanant.schema_name,
                                                     'refresh': refresh, 'access': access, 'refresh_public': refresh_public, 'access_public': access_public},
                                                    status=status.HTTP_200_OK)
                            else:
                                return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'message': 'Tenant is not Active or Suspended'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    check_user.delete()
                    return Response({'message': 'Tenant Not attached, Signup Again'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'message': 'Not an User'}, status=status.HTTP_400_BAD_REQUEST)






class AdminForgetPasswordView(APIView):
    serializer_class = AdminForgetPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context('public'):
            serializer = AdminForgetPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            phone_number = serializer.validated_data['phone_number']
            try:
                check_user = User.objects.get(phone_number=phone_number)
            except:
                check_user = None

            if check_user or check_user is not None:
                try:
                    check_user_teanant = check_user.tenant_user
                except:
                    check_user_teanant = None

                if check_user_teanant or check_user_teanant is not None:
                    if check_user_teanant.is_active:
                        user = User.objects.get(phone_number=phone_number)
                        otp_fetching_metching = ''
                        msg_thread = Thread(target=sendotp, args=(user, schema_name, otp_fetching_metching))
                        msg_thread.start()
                        return Response({'info': 'successful! Otp sent', 'user_id': user.id, 'name': user.name},
                                        status=status.HTTP_201_CREATED)
                    else:
                        return Response({'message': 'Tenant is not Active or Suspended'},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': 'Not an Tenant User'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Not an User'},
                                status=status.HTTP_400_BAD_REQUEST)







class AdminResetPasswordView(APIView):
    serializer_class = AdminResetPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, user_id, *args, **kwargs):
        with schema_context('public'):
            serializer = AdminResetPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            try:
                admin_user_obj = User.objects.get(id=user_id)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                admin_user_obj = None
            try:
                admin_user_otp = OTP.objects.get(receiver=user_id)
            except(TypeError, ValueError, OverflowError, OTP.DoesNotExist):
                admin_user_otp = None
            if admin_user_obj is None or admin_user_otp is None:
                raise ValidationError({'error': 'you are not a valid user'})
            else:
                try:
                    check_user_teanant = admin_user_obj.tenant_user
                except:
                    check_user_teanant = None
                if check_user_teanant or check_user_teanant is not None:
                    if check_user_teanant.is_active:
                        schema_name = check_user_teanant.schema_name
                        if str(admin_user_otp.otp) == str(otp):
                            admin_user_obj.set_password(new_password)
                            admin_user_obj.save()
                            user_phone_number = admin_user_obj.phone_number
                            with schema_context(schema_name):
                                try:
                                    user = User.objects.get(phone_number=user_phone_number, admin=True)
                                except:
                                    user = None
                                if user or user is not None:
                                    user.set_password(new_password)
                                    user.save()
                                else:
                                    return Response({'error': 'User Somehow Deleted From Public Tenant or not an Admin/User in Tenant'})
                            admin_user_otp.delete()
                            return Response({'message': 'Successful', })
                        else:
                            raise ValidationError({'error': 'Invalid OTP'})
                else:
                    return Response({'error': 'Not an Tenant User'},
                                    status=status.HTTP_400_BAD_REQUEST)





class domainChange(APIView):
    """
    To change domain name by the tenant admin
    """
    serializer_class = DomainSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        with schema_context('public'):
            serializer = DomainSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_domain = serializer.validated_data['domain']+'.'+domain_choices
            try:
                check_domain = Domain.objects.get(domain=new_domain)
            except(TypeError, ValueError, OverflowError, Domain.DoesNotExist):
                check_domain = None
            if check_domain or check_domain is not None:
                return Response({'error': 'Domain Already Exist'}, status=status.HTTP_200_OK)
            else:
                if check_domain is None:
                    domain = Domain.objects.get(tenant__user__phone_number=request.user.phone_number)
                    domain.domain = new_domain
                    domain.save()
                    return Response({'Success': 'Domain Created', 'domain': serializer.validated_data['domain']},
                                    status=status.HTTP_201_CREATED)
                return Response({'error': 'Not Admin, '},
                                status=status.HTTP_400_BAD_REQUEST)







