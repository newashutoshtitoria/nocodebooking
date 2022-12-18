from django.urls import re_path
from . import appviews

urlpatterns = [
    #for Signup to APP, with root domain ex-bookeve.in.
    re_path(r'^tenantusersignup/$', appviews.tenantuserSignup.as_view(), name='tenantusersignup'),
    #for validating Signup user mobile number
    re_path(r'^activate/(?P<user_id>[0-9]+)/$', appviews.Activate.as_view(), name='activate'),
    #for sending otp again for signup(new user), or Forget Password
    re_path(r'^resend_otp/(?P<user_id>[0-9]+)/$', appviews.ResendOtp.as_view(), name='resend-otp'),
    #for login to App with mobile number and password. for UserApp.
    re_path(r'^admin_login', appviews.AdminLoginView.as_view(), name='admin_login'),
    #for forget password, that check and send otp to tenant user
    re_path(r'^admin_forget_password/$', appviews.AdminForgetPasswordView.as_view(), name='admin_forget_password'),
    #for setting new password after validating OTP
    re_path(r'^admin_reset_password/(?P<user_id>[0-9]+)/$', appviews.AdminResetPasswordView.as_view(), name='admin_reset_password'),
    #chnage domain name of an tenant
    re_path(r'^domainchange/$', appviews.domainChange.as_view(), name='domainchange'),

]
