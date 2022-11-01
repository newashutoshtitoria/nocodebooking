from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from .models import *


class DomainInline(admin.TabularInline):

    model = Domain
    max_num = 1

@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
        list_display = (
        "user",
        "is_active",
        "created_on",

        )
        inlines = [DomainInline]

admin.site.register(TenantSubscription)
admin.site.register(SubscriptionTransaction)

admin.site.register(ALLTemplate)
admin.site.register(TenantTemplate)
admin.site.register(OtpWallet)