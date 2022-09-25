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
                msg_thread = Thread(target=sendotp, args=(user, schema_name))
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
    """
    change phone number in tenant, if request user is an admin of tenant then mobile number will also change in public schema.
    """
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
    Activate verifies the stored otp and the otp entered by user.phone number can be only change in tenant not in public, but change in both public and tenant if user is admin
    """
    permission_classes = (permissions.IsAuthenticated, IsadminOrIsOwner )
    serializer_class = OTPSerializer

    def post(self, request,user_id, *args,**kwargs):
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

            try:
                receiver_admin = User.objects.get(id=user_id, admin=True)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                receiver_admin = False


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

                if  request_phonenumber or request_phonenumber is not None:
                    new_phone_number = request_phonenumber.phone_number
                    if receiver_admin:
                        with schema_context('public'):
                            try:
                                public_user_obj = User.objects.get(phone_number=receiver.phone_number)
                            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                                public_user_obj = None

                            if public_user_obj or public_user_obj is not None:
                                public_user_obj.phone_number = new_phone_number
                                public_user_obj.save()

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
                    if check_user_teanant.is_active:
                        with schema_context(check_user_teanant.schema_name):
                            serializer = AdminLoginSerializer(data=request.data)
                            serializer.is_valid(raise_exception=True)
                            phone_number = serializer.validated_data['phone_number']
                            password = serializer.validated_data['password']
                            user = User.objects.get(phone_number=phone_number)
                            if user.check_password(password):
                                refresh, access = get_tokens_for_user(user)
                                return Response({'message': 'Successful', 'tenant':check_user_teanant.schema_name,'refresh': refresh, 'access': access},
                                                status=status.HTTP_200_OK)
                            else:
                                return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'message': 'Account is not active or Suspended', 'tenant': check_user_teanant.schema_name},
                                        status=status.HTTP_426_UPGRADE_REQUIRED)
                except:
                    check_user.delete()
                    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Something Bad Happened'}, status=status.HTTP_400_BAD_REQUEST)







class AdminForgetPasswordView(APIView):
    serializer_class = AdminForgetPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            serializer = AdminForgetPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            phone_number = serializer.validated_data['phone_number']
            user = User.objects.get(phone_number=phone_number, admin=True)
            msg_thread = Thread(target=sendotp, args=(user,schema_name))
            msg_thread.start()
            return Response({'info': 'successful! Otp sent', 'user_id': user.id, 'name': user.name},
                            status=status.HTTP_201_CREATED)


class AdminResetPasswordView(APIView):
    serializer_class = AdminResetPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, user_id, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            serializer = AdminResetPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            try:
                admin_user_obj = User.objects.get(id=user_id, admin=True)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                admin_user_obj = None

            try:
                admin_user_otp = OTP.objects.get(receiver=user_id)
            except(TypeError, ValueError, OverflowError, OTP.DoesNotExist):
                admin_user_otp = None


            if admin_user_obj is None or admin_user_otp is None:
                raise ValidationError({'error': 'you are not a valid user'})
            else:
                if str(admin_user_otp.otp) == str(otp):
                    admin_user_obj.set_password(new_password)
                    admin_user_obj.save()

                    with schema_context('public'):
                        user_phone_number = admin_user_obj.phone_number
                        try:
                            user = User.objects.get(phone_number=user_phone_number)
                        except:
                            user = None
                        if user or user is not None:
                            user.set_password(new_password)
                            user.save()
                        else:
                            return Response({'error': 'User Somehow Deleted From Public Tenant'})

                    admin_user_otp.delete()
                    return Response({'message': 'Successful', })
                else:
                    raise ValidationError({'error': 'Invalid OTP'})

class publicForgetPasswordView(APIView):
    serializer_class = publicForgetPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        if schema_name == 'public':
            with schema_context('public'):
                serializer = publicForgetPasswordSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                phone_number = serializer.validated_data['phone_number']
                user = User.objects.get(phone_number=phone_number, admin=False)

                try:
                    check_user_teanant = user.tenant_user
                    if check_user_teanant.is_active:
                        msg_thread = Thread(target=sendotp, args=(user, schema_name))
                        msg_thread.start()
                        return Response({'info': 'successful! Otp sent', 'user_id': user.id, 'name': user.name},
                                        status=status.HTTP_201_CREATED)
                    else:
                        return Response({'message':'Account has suspended or not active'}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    user.delete()
                    return Response({'message':'Account not Exist'}, status=status.HTTP_400_BAD_REQUEST)




        else:
            return Response({'message': 'Not in Public Tenant'}, status=status.HTTP_400_BAD_REQUEST)






class publicResetPasswordView(APIView):
    serializer_class = AdminResetPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, user_id, *args, **kwargs):
        schema_name = connection.schema_name
        if schema_name == 'public':
            with schema_context('public'):
                serializer = AdminResetPasswordSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                otp = serializer.validated_data['otp']
                new_password = serializer.validated_data['new_password']

                try:
                    public_user_obj = User.objects.get(id=user_id, admin=False)
                except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                    public_user_obj = None

                try:
                    public_user_otp = OTP.objects.get(receiver=user_id)
                except(TypeError, ValueError, OverflowError, OTP.DoesNotExist):
                    public_user_otp = None

                if public_user_obj is None or public_user_otp is None:
                    raise ValidationError({'error': 'you are not a valid user'})
                else:
                    if str(public_user_otp.otp) == str(otp):
                        public_user_obj.set_password(new_password)
                        public_user_obj.save()

                        with schema_context(public_user_obj.tenant_user.schema_name):
                            try:
                                user = User.objects.get(phone_number=public_user_obj.phone_number, admin=True)
                            except:
                                user = None

                            if user or user is not None:
                                user.set_password(new_password)
                                user.save()
                            else:
                                return Response({'error': 'Not a Valid User'}, status=status.HTTP_400_BAD_REQUEST)

                        public_user_otp.delete()
                        return Response({'message': 'Sucessfull'}, status=status.HTTP_200_OK)
                    else:
                        raise ValidationError({'error':'Invalid OTP'})




