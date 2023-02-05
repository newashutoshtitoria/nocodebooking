from main.custom_permission import *
from rest_framework import permissions, status
from rest_framework import viewsets
from main.webserializers import CategorySerializer, UserSignupSerializer, OTPSerializer, LoginSerializer, UserAddressSerializer, PackageSerializer, VariantsSerializer, AddOnsSerializer, PriceTagSerializer
from main.models import Category, UserAddress, PriceTag, Package, Carousel, Checkout, PackageCheckout, DiscountedCoupons, AddOns, Variants
from users.models import User, OTP
from django.db import connection
from django_tenants.utils import schema_context
from rest_framework.views import APIView
from messages.SendOTP import sendotp
from threading import Thread
from rest_framework.response import Response
from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import login, logout
from users.token import get_tokens_for_user
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import base64
from django.db import connection
from django_tenants.utils import schema_context
from tenant.models import Tenant
from rest_framework import generics
from rest_framework.parsers import JSONParser
import datetime
import pytz
import json


class CategoryView(viewsets.ModelViewSet):
    """
    This View is for  of Category.
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (permissions.AllowAny, IstenantuserOrReadOnly)



class PackageView(viewsets.ModelViewSet):
    """
    This View is for  of Packages.
    """
    serializer_class = PackageSerializer
    queryset = Package.objects.all()
    permission_classes = (permissions.AllowAny, IstenantuserOrReadOnly)


class CategoryPackageView(APIView):
    def get(self, request, format=None):
        categories = Category.objects.all()

        data = [{"category": c.category, "packages": [
            {
                "icon":  request.build_absolute_uri(p.icon.url) if p.icon else '',
                "package_name": p.package_name,
                "original_price": p.original_price,
                "offering_price": p.offering_price,
                "description": p.description,
                "total_time": p.total_time,
                "offer": p.offer,
                "created_on": p.created_on,
                "variants": VariantsSerializer(p.package_variants.all(), many=True).data,
                "addons": AddOnsSerializer(p.package_addons.all(), many=True).data,
                "price_tag": PriceTagSerializer(p.price_tag).data,
            }
            for p in c.category_package.filter(status=True)
        ]} for c in categories]
        return Response(data)



class AlldataView(APIView):
    def get(self, request, format=None):
        data = []
        company = {}
        company_obj = {}
        schema_name = connection.schema_name
        with schema_context(schema_name):
            tenant = Tenant.objects.get(schema_name=schema_name)
            try:
                account_inform = tenant.teant_account_information
                company_obj["company_name"] = tenant.company_name
                company_obj["company_logo"] = request.build_absolute_uri(
                    tenant.company_logo.url) if tenant.company_logo else '',
                company_obj["about"] = account_inform.about
                company_obj["location"] = account_inform.location
                company_obj["instagram"] = account_inform.instagram
                company_obj["facebook"] = account_inform.facebook
                company_obj["youtube"] = account_inform.youtube
                company_obj["whatsapp"] = account_inform.whatsapp
                company_obj["bussiness_category"] = account_inform.bussiness_category
                company_obj["email"] = account_inform.email
            except:
                pass



            try:
                tenant_subs = tenant.teant_subscriptions
                if tenant_subs.subscription.plan.tags.filter(tag__iexact="free"):
                    company_obj["promation"] = "yes"
            except:
                pass


            company_obj["is_active"] = "inactive"
            if tenant.is_active:
                company_obj["is_active"] = "active"

        company["company"] = company_obj

        data.append(company)

        categories = Category.objects.all()
        carousel = Carousel.objects.filter(status=True).order_by('order_by')


        categories = {'categoryes' : [
            {
                "category": c.category,
                 "category_icon": request.build_absolute_uri(c.icon.url) if c.icon else '',
                 "packages": [
           {
                "icon":  request.build_absolute_uri(p.icon.url) if p.icon else '',
                "package_name": p.package_name,
                "original_price": p.original_price,
                "offering_price": p.offering_price,
                "description": p.description,
                "total_time": p.total_time,
                "offer": p.offer,
                "created_on": p.created_on,
                "variants": VariantsSerializer(p.package_variants.all(), many=True).data,
                "addons": AddOnsSerializer(p.package_addons.all(), many=True).data,
                "price_tag": PriceTagSerializer(p.price_tag).data,
            }
            for p in c.category_package.filter(status=True)
        ]} for c in categories
        ]}

        data.append(categories)

        if carousel:
            data.append({
                "carousels": [{
                   "carousel_img": request.build_absolute_uri(p.carousel_img.url) if p.carousel_img else '',
                    "select_type": p.select_type,
                    "select_type_ids": p.select_type_ids,
                    "link": p.link,
                    "get_select_type": [
                        {"obj":obj.id,
                         "icon": request.build_absolute_uri(obj.icon.url) if obj.icon else '',
                         "package_name": obj.package_name,
                         "original_price": obj.original_price,
                         "offering_price": obj.offering_price,
                         "description": obj.description,
                         "total_time": obj.total_time,
                         "offer": obj.offer,
                         "created_on": obj.created_on,
                         "variants": VariantsSerializer(obj.package_variants.all(), many=True).data,
                         "addons": AddOnsSerializer(obj.package_addons.all(), many=True).data,
                         "price_tag": PriceTagSerializer(obj.price_tag).data,

                         }
                        if p.select_type=='package' else
                        {}

                    if p.select_type=='category' else {}
                        for obj in p.get_select_type
                    ],

                } for p in carousel]
            })

        return Response(data)






class Signup(APIView):
    """
    View for sign up.
    """
    serializer_class = UserSignupSerializer
    permission_classes = (permissions.AllowAny,)

    @atomic
    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            serializer = UserSignupSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                phone_number = serializer.validated_data['phone_number']
                name = serializer.validated_data['name']
                otp_fetching_metching = serializer.validated_data['otp_fetching_metching']
                user = User.objects.create_user(phone_number=phone_number, name=name)

                msg_thread = Thread(target=sendotp, args=(user,schema_name,otp_fetching_metching))
                msg_thread.start()
                user.save()
                return Response({'info': 'Successfully signed-up', 'user_id': user.id, 'name': name},
                                status=status.HTTP_201_CREATED)
            raise ValidationError({'error': 'Invalid User'})


class Activate(APIView):
    """
    Activate verifies the stored otp and the otp entered by user.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = OTPSerializer

    def post(self, request, user_id,*args,**kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            serializer = OTPSerializer(data=request.data)
            code_otp = request.data['otp']
            try:
                otp = OTP.objects.get(receiver=user_id)
            except(TypeError, ValueError, OverflowError, OTP.DoesNotExist):
                otp = None
            try:
                receiver = User.objects.get(id=user_id)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                receiver = None


            if otp is None or receiver is None:
                raise ValidationError({'error': 'you are not a valid user'})
            elif timezone.now() - otp.sent_on >= timedelta(days=0, hours=0, minutes=1, seconds=0):
                # otp.delete()
                raise ValidationError({'error': 'OTP expired!'})

            if str(otp.otp) == str(code_otp):
                if receiver.active is False:
                    serializer.is_valid(raise_exception=True)
                    receiver.active = True
                    receiver.save()
                otp.delete()
                refresh, access = get_tokens_for_user(receiver, schema_name)
                return Response({'message': 'Successful', 'refresh': refresh, 'access': access})
            else:
                raise ValidationError({'error': 'Invalid OTP'})


class ResendOtp(APIView):
    """
    views for resend the otp.
    """
    serializer_class = OTPSerializer
    permission_classes = (permissions.AllowAny,)

    def get(self, request, user_id, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            try:
                user = User.objects.get(id=user_id)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            if user is None:
                raise ValidationError({'error': 'Not a valid user!'})
            otp_fetching_metching = None
            msg_thread = Thread(target=sendotp, args=(user, schema_name,otp_fetching_metching))
            msg_thread.start()
            return Response({'info': 'Resent OTP', 'user_id': user.id, 'name': user.name},
                            status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    User for logging in.
    """
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            phone_number = serializer.validated_data['phone_number']
            otp_fetching_metching = serializer.validated_data['otp_fetching_metching']
            user = User.objects.get(phone_number=phone_number)
            msg_thread = Thread(target=sendotp, args=(user, schema_name,otp_fetching_metching))
            msg_thread.start()
            return Response({'info': 'successful! Otp sent', 'user_id': user.id, 'name': user.name},
                            status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    logout view.Only authenticated user can access this url(by default)
    """
    def get(self, request, *args, **kwargs):
        logout(request)
        return Response({'message':'successfully logged out'},
                        status=status.HTTP_200_OK)


class ProfileView(APIView):
    """
    Profile View of User.
    """
    serializer_class = UserSignupSerializer
    permission_classes = (permissions.AllowAny,permissions.IsAuthenticated)

    def get(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            try:
                user_id = self.request.user.id
                user = User.objects.get(id=user_id)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            if user:
                serializer = UserSignupSerializer(data={"phone_number": user.phone_number, "name": user.name})
                serializer.is_valid()
                return Response(serializer.data)
            raise ValidationError({'error': 'Not a valid user'})



class UserAddressView(viewsets.ModelViewSet):
    """
    View for handling User's address i.e CRUD.
    """
    serializer_class = UserAddressSerializer
    permission_classes = (permissions.IsAuthenticated, IsUser)
    queryset = UserAddress.objects.all()

    def list(self, request):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            queryset = UserAddress.objects.filter(user=request.user.id)
            serializer = UserAddressSerializer(queryset, many=True)
            return Response(serializer.data)

    def perform_create(self, serializer):
        schema_name = connection.schema_name
        with schema_context(schema_name):
            user = self.request.user
            count = UserAddress.objects.filter(user=user).count()
            if count == 4:
                raise ValidationError({'error': "Not Allowed"})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user)





class CheckoutCreateAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        address = request.data.get("address")
        coupon = request.data.get("coupon")
        appointment_date_str = request.data.get("appointment_date")
        appointment_date_x = datetime.datetime.strptime(appointment_date_str, '%Y-%m-%dT%H:%M:%S')
        appointment_date_y = pytz.utc.localize(appointment_date_x)

        checkout_data = request.data.get('checkout')
        checkout = Checkout.objects.create(user=user)
        checkout.address = address
        checkout.package_stages = 'Pending'
        checkout.payment_stages = 'Not Initiated'

        checkout.appointment_date = appointment_date_y

        checkout.save()
        amnountlist= []

        if checkout_data:
            for package_f in checkout_data:
                amt = 0
                pkg_checkout = PackageCheckout.objects.create()
                package_obj = Package.objects.get(id=package_f['package'])
                pkg_checkout.packages = package_obj
                pkg_checkout.checkout = checkout

                try:
                    if package_f['add-on']:
                        for addon_f in package_f['add-on']:

                            addon_obj = AddOns.objects.get(id=addon_f)
                            pkg_amount = addon_obj.additional_price
                            amt = amt+pkg_amount
                            pkg_checkout.addon.add(addon_obj)

                except:
                    pass

                try:
                    if package_f['variants']:
                        variant_obj = Variants.objects.get(id=package_f['variants'])
                        pkg_checkout.variants = variant_obj
                        amt = amt+variant_obj.offering_price
                    else:
                        amt = amt+package_obj.offering_price
                except:
                    amt = amt+package_obj.offering_price
                amnountlist.append(amt)
                pkg_checkout.save()

        offeredprice_withoutdiscount = sum(amnountlist)

        if coupon:
            try:
                discounted_coupons =DiscountedCoupons.objects.get(id=coupon)
                try:
                    discountedvalue = discounted_coupons.check_validity(offeredprice_withoutdiscount)
                    checkout.price_paid = discountedvalue
                except:
                    return ValidationError("Discount Coupon isn't Valid")

                checkout.coupon = discounted_coupons
                checkout.save()
            except:
                pass

        return Response({'info': 'successful! Checkout', 'checkout_id': checkout.id},
                        status=status.HTTP_201_CREATED)

