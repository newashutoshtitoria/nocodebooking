import requests
import os
from users.models import OTP
from random import *
from django_tenants.utils import schema_context

def sendotp(user, schema_name, otp_fetching_metching):
    with schema_context(schema_name):
        try:
            otp = OTP.objects.filter(receiver=user)
        except(TypeError, ValueError, OverflowError, OTP.DoesNotExist):
            otp = None

        if otp is not None:
            otp.delete()

        # otp = randint(1000, 9999)
        otp = 4444

        data = OTP.objects.create(otp=otp, receiver=user)
        data.save()

        YOUR_AUTH_KEY = "m67JEb9QGH8hLPf0KMC3alqzWjFBrIS5sVRZwONDxvdc1ni2XYGUdZh3ToK02ysS6xD5ezMHCicfXYNF"
        url = "https://www.fast2sms.com/dev/bulk"

        payload = "sender_id=WOFOCR&language=english&route=qt&numbers=" + str(
            user.phone_number) + "&message=16920&variables={#EE#}|{#AA#}&variables_values=" + str(
            user.name) + "|" + str(otp)
        headers = {
            'authorization': YOUR_AUTH_KEY,
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache",
        }
        response = requests.request("POST", url, data=payload, headers=headers)


def phonechangeotp(user, schema_name, phone_number):
    with schema_context(schema_name):
        try:
            otp = OTP.objects.filter(receiver=user)
        except(TypeError, ValueError, OverflowError, OTP.DoesNotExist):
            otp = None

        if otp is not None:
            otp.delete()

        # otp = randint(1000, 9999)
        otp = 4444
        data = OTP.objects.create(otp=otp, receiver=user)
        data.save()



        # YOUR_AUTH_KEY = "m67JEb9QGH8hLPf0KMC3alqzWjFBrIS5sVRZwONDxvdc1ni2XYGUdZh3ToK02ysS6xD5ezMHCicfXYNF"
        # url = "https://www.fast2sms.com/dev/bulk"
        #
        # payload = "sender_id=WOFOCR&language=english&route=qt&numbers=" + str(phone_number) + "&message=16920&variables={#EE#}|{#AA#}&variables_values=" + str(
        #     user.name) + "|" + str(otp)
        # headers = {
        #     'authorization': YOUR_AUTH_KEY,
        #     'Content-Type': "application/x-www-form-urlencoded",
        #     'Cache-Control': "no-cache",
        # }
        # response = requests.request("POST", url, data=payload, headers=headers)






