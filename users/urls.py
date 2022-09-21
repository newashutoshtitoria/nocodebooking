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

    #re_path(r'^admin_login', views.AdminLoginView.as_view(), name='admin_login'),


]
