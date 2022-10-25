from django.urls import re_path
from . import views


urlpatterns = [
    re_path(r'^createcompany/$', views.createCompany.as_view(), name='createCompany'),
    re_path(r'^tenatsubscription/$', views.tenatsubscription.as_view(), name='tenatsubscription'),

]