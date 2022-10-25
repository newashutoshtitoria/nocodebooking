from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
import re

User = get_user_model()

class TenantSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'}
    )

    class Meta:
        model = Tenant
        fields='__all__'

    def validate(self, data):
        return data


class TenantSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TenantSubscription
        # fields = '__all__'
        exclude = ['user', 'teant_attched']

    def validate(self, data):
        return data


