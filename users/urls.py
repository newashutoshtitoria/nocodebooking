from django.urls import re_path
from . import views




urlpatterns = [
    re_path(r'^signup/$', views.Signup.as_view(), name='register'),
    re_path(r'^login/$', views.LoginView.as_view(), name='login'),
    re_path(r'logout/$', views.LogoutView.as_view(), name='logout'),
    re_path(r'^activate/(?P<user_id>[0-9]+)/$', views.Activate.as_view(), name='activate'),
    re_path(r'^userdetail/$', views.userdetail.as_view(), name='userdetail'),
    # re_path(r'^gettenantdetails/$', views.gettenantdetails.as_view(), name='gettenantdetails'),
    re_path(r'^resend_otp/(?P<user_id>[0-9]+)/$', views.ResendOtp.as_view(), name='resend-otp'),
    re_path(r'^changephonenumber/$', views.changephonenumber.as_view(), name='changephonenumber'),
    re_path(r'^newphone_validate/(?P<user_id>[0-9]+)/$', views.newphone_validate.as_view(), name='newphone_validate'),
    re_path(r'^admin_login', views.AdminLoginView.as_view(), name='admin_login'),
    re_path(r'^admin_forget_password/$', views.AdminForgetPasswordView.as_view(), name='admin_forget_password'),
    re_path(r'^admin_reset_password/(?P<user_id>[0-9]+)/$', views.AdminResetPasswordView.as_view(), name='admin_reset_password'),
    re_path(r'^tenantusersignup/$', views.tenantuserSignup.as_view(), name='tenantusersignup'),

    #public user password
    re_path(r'^public_forget_password/$', views.publicForgetPasswordView.as_view(), name='public_forget_password'),
    re_path(r'^public_reset_password/(?P<user_id>[0-9]+)/$', views.publicResetPasswordView.as_view(), name='public_reset_password'),

    #chnage domain name of an tenant
    re_path(r'^domainchange/$', views.domainChange.as_view(), name='domainchange'),

]
