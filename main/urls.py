from django.urls import re_path
from . import views


urlpatterns = [
    re_path(r'^user/$', views.Signup.as_view(), name='Signup'),

]