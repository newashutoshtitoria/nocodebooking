from django.db import models
from core.settings import AUTH_USER_MODEL
from django_tenants.models import DomainMixin, TenantMixin
from subscriptionplansg.models import *
from django.db import connection
from django_tenants.utils import schema_context
from django.core.validators import MinLengthValidator


class Tenant(TenantMixin):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='tenant_user')
    company_name = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=False, blank=True)
    created_on = models.DateField(auto_now_add=True)
    auto_create_schema = True
    auto_drop_schema = True



class Domain(DomainMixin):
    pass

class ALLTemplate(models.Model):
    name = models.CharField(max_length=30)
    template_code = models.CharField(null=False, blank=False, unique=True, max_length=6, validators=[MinLengthValidator(6)])
    date = models.DateTimeField(default=datetime.now(),blank=True,null=True,verbose_name='start date')
    paid_template = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    def __str__(self):
        if self.active:
            return self.name+' Active, paid template '+ str(self.paid_template)
        else:
            return self.name+' inactive, paid template '+ str(self.paid_template)

    def save(self, *args, **kwargs):
        schema_name = connection.schema_name
        if schema_name == 'public':
            super(ALLTemplate, self).save(*args, **kwargs)


class TenantTemplate(models.Model):
    templates = models.ForeignKey(ALLTemplate, null=True, on_delete=models.CASCADE, related_name='teant_attached_template')
    teant_attched = models.OneToOneField(Tenant, null=True, on_delete=models.CASCADE, related_name='teant_template')
    date = models.DateTimeField(default=datetime.now(),blank=True,null=True,verbose_name='start date')
    active = models.BooleanField(default=False)

    def __str__(self):
        try:
            return str(self.teant_attched.company_name)+' '+ str(self.templates)
        except:
            return ''


# Tenant Subscription
class TenantSubscription(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL,null=True,on_delete=models.CASCADE,related_name='subscriptions')
    teant_attched = models.OneToOneField(Tenant, null=True, on_delete=models.CASCADE, related_name='teant_subscriptions')
    subscription = models.ForeignKey(PlanCost,null=True,on_delete=models.CASCADE, related_name='subscriptions')
    date_billing_start = models.DateTimeField(default=datetime.now(),blank=True,null=True,verbose_name='billing start date')
    date_billing_end = models.DateTimeField(blank=True,null=True,verbose_name='billing start end')
    payment = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)

    class Meta:
        ordering = ('user', 'date_billing_start',)

    def save(self, *args, **kwargs):
        self.date_billing_end = self.subscription.next_billing_datetime(self.date_billing_start)
        super(TenantSubscription, self).save(*args, **kwargs)


class SubscriptionTransaction(models.Model):
    """Details for a subscription plan billing."""

    user = models.ForeignKey(
        AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name='subscription_transactions'
    )
    teant_attched = models.ForeignKey(Tenant, null=True, on_delete=models.CASCADE, related_name='teant_subscriptions_transection')

    subscription = models.ForeignKey(
        PlanCost,
        null=True,
        on_delete=models.SET_NULL,
        related_name='transactions'
    )
    date_transaction = models.DateTimeField(
        default=datetime.now(),
        verbose_name='transaction date',
    )
    amount = models.DecimalField(
        blank=True,
        decimal_places=4,
        max_digits=19,
        null=True,
    )

    amount_paid = models.DecimalField(
        blank=True,
        decimal_places=4,
        max_digits=19,
        null=True,
    )

    class Meta:
        ordering = ('date_transaction', 'user',)


class OtpWallet(models.Model):
    """Details for a otp wallet plan billing."""

    user = models.OneToOneField(
        AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name='otp_user'
    )
    teant_attched = models.ForeignKey(Tenant, null=True, on_delete=models.CASCADE, related_name='teant_otp')


    date_transaction = models.DateTimeField(
        default=datetime.now(),
        verbose_name='transaction date',
    )
    total_otp_credit = models.DecimalField(
        blank=True,
        decimal_places=0,
        max_digits=4,
        null=True,
    )

    __current_credit = None



    class Meta:
        ordering = ('date_transaction', 'user',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__current_credit = self.total_otp_credit

    def save(self, *args, **kwargs):
        schema_name = connection.schema_name
        if schema_name == 'public':
            if self.pk is None:
                if self.__current_credit or not None:
                    self.total_otp_credit =  self.total_otp_credit
                    super(OtpWallet, self).save(*args, **kwargs)
            else:
                if self.__current_credit or not None:
                    self.total_otp_credit = self.__current_credit + self.total_otp_credit
                    super(OtpWallet, self).save(*args, **kwargs)

