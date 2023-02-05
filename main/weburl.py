from django.urls import re_path
from . import webviews
from django.urls import include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'category', webviews.CategoryView)
router.register(r'packages', webviews.PackageView)
router.register(r'address', webviews.UserAddressView)

urlpatterns = [
    re_path(r'', include(router.urls)),
    re_path(r'^signup/$', webviews.Signup.as_view(), name='register'),
    re_path(r'^activate/(?P<user_id>[0-9]+)/$', webviews.Activate.as_view(), name='activate'),
    re_path(r'^resend_otp/(?P<user_id>[0-9]+)/$', webviews.ResendOtp.as_view(), name='resend-otp'),
    re_path(r'^login/$', webviews.LoginView.as_view(), name='login'),
    re_path(r'logout/$', webviews.LogoutView.as_view(), name='logout'),
    re_path(r'^me/$', webviews.ProfileView.as_view(), name='profile'),

    re_path('categories/', webviews.CategoryPackageView.as_view(), name='category_package_view'),
    re_path('alldata/', webviews.AlldataView.as_view(), name='alldata_view'),

    re_path('checkouts/', webviews.CheckoutCreateAPIView.as_view(), name='checkout-list'),

]