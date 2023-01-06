from django.urls import re_path
from . import views


urlpatterns = [
    re_path(r'^user/$', views.Signup.as_view(), name='Signup'),
    re_path(r'^activate/(?P<user_id>[0-9]+)/$', views.Activate.as_view(), name='activate'),

]