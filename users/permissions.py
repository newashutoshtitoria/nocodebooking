from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS
from django.db import connection
from django_tenants.utils import schema_context
from .models import *
import jwt
from core.settings import SECRET_KEY



class IsUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user.id == request.user.id


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.admin


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = User.objects.filter(pk=request.user.id, admin=True)
        if user:
            return True
        return False


class IsadminOrIsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.user.id == request.user.id or request.user.is_admin:
            return False
        else:
            return False


#tenant users


class istenantuser(permissions.BasePermission):
    def has_permission(self, request, view):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            payload_jwt_schema_name = jwt.decode(str(request.auth), SECRET_KEY, algorithms=["HS512"])['schema_name']
            if schema_name == payload_jwt_schema_name:
                if request.user:
                    return True
        return False




