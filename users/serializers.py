from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from .models import *
import re

User = get_user_model()


class UserSignupSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True, allow_blank=False, allow_null=False,)
    name = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    class Meta:
        model = User
        fields = ('phone_number', 'name')

    def validate(self, data):
        phone = data.get('phone_number')
        try:
            phone_number = User.objects.filter(phone_number=phone)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            phone_number=None
        if phone_number:
            raise ValidationError({"error": "phone number already exists"})
        if phone:
            phone_regex = "^[6789]\d{9}$"
            phone_valid = re.compile(phone_regex)
            if not phone_valid.match(phone):
                raise ValidationError({"error": "Invalid Phone number"})
            else:
                return data
        raise ValidationError({"error": "Invalid Phone number"})

class TenantUserSignupSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True, allow_blank=False, allow_null=False,)
    name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    password = serializers.CharField(
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('phone_number', 'name', 'password', 'confirm_password')

    def validate(self, data):
        phone_number = data.get('phone_number')
        new_password = data.get('password')
        confirm_password = data.get('confirm_password')
        try:
            user = User.objects.filter(phone_number=phone_number)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user=None

        if user:
            raise ValidationError({"error": "phone number already exists"})

        if phone_number:
            phone_regex = "^[6789]\d{9}$"
            phone_valid = re.compile(phone_regex)
            if not phone_valid.match(phone_number):
                raise ValidationError({"error": "Invalid Phone number"})
            else:
                if new_password != confirm_password:
                    raise ValidationError({"error": "Passwords don't match"})
                else:
                    return data
        raise ValidationError({"error": "Invalid Phone number"})


class OTPSerializer(serializers.ModelSerializer):
    """
    serializer for otp
    """
    class Meta:
        model = OTP
        fields = ['otp']

    def validate(self, data):
        otp = data.get('otp')
        if len(str(otp)) != 4:
            raise ValidationError({"error":"Invalid OTP"})
        else:
            return data

class LoginSerializer(serializers.ModelSerializer):
    """serializer for Login using otp"""
    phone_number = serializers.CharField(validators=None)

    class Meta:
        model = User
        fields = ['phone_number', ]

    def validate(self,data):
        phone_number = data.get('phone_number')
        if phone_number:
            phone_regex = "^[6789]\d{9}$"
            phone_valid = re.compile(phone_regex)
        if not phone_valid.match(phone_number):
            raise ValidationError({"error": "Invalid Phone number"})
        try:
            user = User.objects.get(phone_number=phone_number)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if not user or user is None:
            raise ValidationError({'error': "Phone number doesn't exist"})
        return data

class phonenumberchangeserializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=None)

    class Meta:
        model = requestednewphonenumber
        fields = ['phone_number', ]

    def validate(self,data):
        phone_number = data.get('phone_number')
        if phone_number:
            phone_regex = "^[6789]\d{9}$"
            phone_valid = re.compile(phone_regex)

        if not phone_valid.match(phone_number):
            raise ValidationError({"error": "Invalid Phone number"})

        try:
            user = User.objects.get(phone_number=phone_number)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user or user is not None:
            raise ValidationError({'error': "Phone number exist"})

        return data


class AdminLoginSerializer(serializers.ModelSerializer):

    phone_number = serializers.CharField(validators=None)
    password = serializers.CharField(
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['phone_number', 'password']

    def validate(self, data):
        phone_number = data.get('phone_number')
        try:
            user = User.objects.get(phone_number=phone_number, admin=True)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if not user:
            raise ValidationError({'error': "Entry restricted, Not an admin"})
        return data


class AdminForgetPasswordSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=None)

    class Meta:
        model = User
        fields = ['phone_number', ]

    def validate(self,data):
        phone_number = data.get('phone_number')
        if phone_number:
            phone_regex = "^[6789]\d{9}$"
            phone_valid = re.compile(phone_regex)
        if not phone_valid.match(phone_number):
            raise ValidationError({"error": "Invalid Phone number"})
        try:
            user = User.objects.get(phone_number=phone_number, admin=True)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if not user or user is None:
            raise ValidationError({'error': "Not an Admin User"})
        return data


class AdminResetPasswordSerializer(serializers.ModelSerializer):

    new_password = serializers.CharField(
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        style={'input_type': 'password'}
    )
    class Meta:
        model = OTP
        fields = ['otp', 'new_password', 'confirm_password',]

    def validate(self, data):
        otp = data.get('otp')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        print(new_password)
        print(confirm_password)
        if len(str(otp)) != 4:
            raise ValidationError({"error":"Invalid OTP"})
        else:
            if new_password != confirm_password:
                raise ValidationError({"error":"Passwords don't match"})
            else:
                return data


class publicForgetPasswordSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=None)

    class Meta:
        model = User
        fields = ['phone_number', ]

    def validate(self,data):
        phone_number = data.get('phone_number')
        if phone_number:
            phone_regex = "^[6789]\d{9}$"
            phone_valid = re.compile(phone_regex)
        if not phone_valid.match(phone_number):
            raise ValidationError({"error": "Invalid Phone number"})
        try:
            user = User.objects.get(phone_number=phone_number)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if not user or user is None:
            raise ValidationError({'error': "Not an User"})
        return data