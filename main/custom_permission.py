from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS
from django.db import connection
from django_tenants.utils import schema_context
from core.settings import AUTH_USER_MODEL
import jwt
from core.settings import SECRET_KEY

class IsUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user.id == request.user.id

class IstenantuserOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        current_schema_name = connection.schema_name

        try:
            phone_number_f = request.user.phone_number
        except:
            phone_number_f = None

        if request.method in permissions.SAFE_METHODS:
            return True
        if phone_number_f:
            with schema_context('public'):
                try:
                    check_user = User.objects.get(phone_number=phone_number_f)
                except:
                    check_user = None
                if check_user:
                    if check_user or check_user is not None:
                        try:
                            check_user_teanant = check_user.tenant_user
                        except:
                            check_user_teanant = None

                        if check_user_teanant or check_user_teanant is not None:
                            if check_user_teanant.is_active:
                                schema_name = check_user_teanant.schema_name
                                if current_schema_name == schema_name:
                                    return True
                                else:
                                    return False
                        else:
                            return False
                    return False
                return False
        return False
