from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
import re

User = get_user_model()

class TenantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tenant
        fields='__all__'

    def validate(self, data):
        return data