from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(PriceTag)
admin.site.register(Package)
admin.site.register(Variants)
admin.site.register(AddOns)
admin.site.register(Carousel)
admin.site.register(DiscountedCoupons)
admin.site.register(UserAddress)
admin.site.register(Checkout)
admin.site.register(PackageCheckout)


