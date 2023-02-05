from rest_framework import serializers
from main.models import Category, UserAddress, PriceTag, Package, Variants, Checkout, PackageCheckout
import re
from rest_framework.exceptions import ValidationError
from django.db import connection
from django_tenants.utils import schema_context
from users.models import OTP
from django.contrib.auth import get_user_model
User = get_user_model()


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ('status',)


class VariantsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    variant = serializers.CharField()
    original_price = serializers.FloatField()
    offering_price = serializers.FloatField()

class AddOnsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    add_on_name = serializers.CharField()
    additional_price = serializers.FloatField()

class PriceTagSerializer(serializers.Serializer):
    price_tag = serializers.CharField()








class UserSignupSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True, allow_blank=False, allow_null=False,)
    name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    otp_fetching_metching = serializers.CharField()

    class Meta:
        model = User
        fields = ('phone_number', 'name', 'otp_fetching_metching')

    def validate(self, data):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            phone = data.get('phone_number')
            try:
                phone_number = User.objects.filter(phone_number=phone)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                phone_number = None
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
            return data



class LoginSerializer(serializers.ModelSerializer):
    """serializer for Login using otp"""
    phone_number = serializers.CharField(validators=None)
    otp_fetching_metching = serializers.CharField()

    class Meta:
        model = User
        fields = ['phone_number', 'otp_fetching_metching']

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


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = '__all__'
        read_only_fields = ('user',)

    def validate(self, data):
        regex = r"^[1-9][0-9]{5}$"
        pincode = data.get('postal_code')
        if re.match(regex, pincode):
            return data
        raise ValidationError({"error": "Invalid pincode   "})








