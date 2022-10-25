from django.db import models
from core.settings import AUTH_USER_MODEL
from django_tenants.models import DomainMixin, TenantMixin
from subscriptionplansg.models import *

class Tenant(TenantMixin):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='tenant_user')
    company_name = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=False, blank=True)
    created_on = models.DateField(auto_now_add=True)
    auto_create_schema = True
    auto_drop_schema = True


class Domain(DomainMixin):
    pass

class TenantSubscription(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL,null=True,on_delete=models.CASCADE,related_name='subscriptions')
    teant_attched = models.ForeignKey(Tenant, null=True, on_delete=models.CASCADE, related_name='teant_subscriptions')
    subscription = models.ForeignKey(PlanCost,null=True,on_delete=models.CASCADE, related_name='subscriptions')
    date_billing_start = models.DateTimeField(blank=True,null=True,verbose_name='billing start date')
    date_billing_end = models.DateTimeField(blank=True,null=True,verbose_name='billing start end')
    date_billing_last = models.DateTimeField(blank=True,null=True,verbose_name='last billing date')
    date_billing_next = models.DateTimeField(blank=True,null=True,verbose_name='next start date',)
    active = models.BooleanField(default=True)
    cancelled = models.BooleanField(default=False)

    class Meta:
        ordering = ('user', 'date_billing_start',)


class SubscriptionTransaction(models.Model):
    """Details for a subscription plan billing."""

    user = models.ForeignKey(
        AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name='subscription_transactions'
    )
    subscription = models.ForeignKey(
        PlanCost,
        null=True,
        on_delete=models.SET_NULL,
        related_name='transactions'
    )
    date_transaction = models.DateTimeField(
        verbose_name='transaction date',
    )
    amount = models.DecimalField(
        blank=True,
        decimal_places=4,
        max_digits=19,
        null=True,
    )

    class Meta:
        ordering = ('date_transaction', 'user',)

