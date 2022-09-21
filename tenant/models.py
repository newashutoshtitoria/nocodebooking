from django.db import models
from core.settings import AUTH_USER_MODEL
from django_tenants.models import DomainMixin, TenantMixin



class businessPlan(models.Model):
    plan_name =  models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=False, blank=True)
    price = models.CharField(max_length=50, null=True, blank=True)
    days = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.plan_name



class Tenant(TenantMixin):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='tenant_user')
    company_name = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=False, blank=True)
    # trial_expired = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)

    auto_create_schema = True
    auto_drop_schema = True





class Domain(DomainMixin):
    pass
