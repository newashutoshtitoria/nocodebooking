from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import OTP
from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from main.models import *
import re

User = get_user_model()



class UserSignupSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True, allow_blank=False, allow_null=False,)
    name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    otp_fetching_metching = serializers.CharField()

    class Meta:
        model = User
        fields = ('phone_number', 'name', 'otp_fetching_metching')

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
            return