from .landingview import *
from django.urls import path

app_name = 'webapp'

urlpatterns = [
    path('login', login, name='login' ),
    ]