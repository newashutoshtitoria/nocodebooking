from rest_framework import permissions
from rest_framework.views import APIView
from .serializers import TenantSerializer, TenantSubscriptionSerializer, TenantTemplateSerializer, OtpWalletSerializer
from .models import *
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from django_tenants.utils import schema_context
from users.models import User
from .task import createcompany, createcompanynocelery
from django.db import connection
from django_tenants.utils import schema_context
from django.utils import timezone
from subscriptionplansg.models import *
from django.utils.decorators import method_decorator
from django.db.transaction import atomic
from rest_framework import generics, viewsets, mixins


class createCompany(APIView):
    serializer_class = TenantSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        if schema_name == 'public':
            serializer = TenantSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                schema_name = serializer.validated_data['schema_name']
                user = request.user
                company_name = serializer.validated_data['company_name']
                data = {
                    'schema_name': schema_name,
                    'user': user.id,
                    'company_name': company_name,
                }
                #without celery
                if createcompanynocelery(data):
                    return Response({'info': 'Successfully signed-up'}, status=status.HTTP_201_CREATED)

                #with celery
                # if createcompany.delay(data):
                #     return Response({'info': 'Successfully signed-up'}, status=status.HTTP_201_CREATED)
        raise ValidationError({'error': 'something bad happens, you can create a site'})



@method_decorator(atomic, name='dispatch')
class tenatsubscription(APIView):
    serializer_class = TenantSubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        if schema_name == 'public':
            serializer = TenantSubscriptionSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                subscription_obj = serializer.validated_data['subscription']
                amountpaid = serializer.validated_data['amountpaid']
                user_s = request.user
                #get schema name
                try:
                    check_user_teanant = user_s.tenant_user
                except:
                    check_user_teanant = None

                if check_user_teanant or check_user_teanant is not None:
                    # check subscription plan
                    try:
                        tenant_sub_plan = check_user_teanant.teant_subscriptions
                    except:
                        tenant_sub_plan = None

                    # check subscription plan is active
                    if tenant_sub_plan:
                        if tenant_sub_plan.date_billing_end - timezone.now() >= timedelta(days=0, hours=0, minutes=0, seconds=0):
                            return Response({'message': 'You Already have plan'})
                        else:
                            #as plan expired, we are delting tenant subscription data
                            check_user_teanant.teant_subscriptions.all().delete()
                            new_subscription = TenantSubscription.objects.create(user=user_s,teant_attched= check_user_teanant, subscription = subscription_obj)
                            new_subscription.payment = True
                            new_subscription.save()

                            #creating transaction for history

                            SubscriptionTransaction.objects.create(
                                user = user_s,
                                teant_attched = check_user_teanant,
                                subscription = subscription_obj,
                                amount = subscription_obj.cost,
                                amount_paid = amountpaid,

                            )
                            return Response({'message': 'Successfully'}, status= status.HTTP_201_CREATED)
                    else:
                        new_subscription = TenantSubscription.objects.create(user=user_s,
                                                                             teant_attched=check_user_teanant,
                                                                             subscription=subscription_obj)
                        new_subscription.payment = True
                        new_subscription.save()

                        # creating transaction for history

                        SubscriptionTransaction.objects.create(
                            user=user_s,
                            teant_attched=check_user_teanant,
                            subscription=subscription_obj,
                            amount=subscription_obj.cost,
                            amount_paid=amountpaid,

                        )
                        return Response({'message': 'Successfully'}, status=status.HTTP_201_CREATED)

                return Response({'error':'User have no Tenant'}, status= status.HTTP_406_NOT_ACCEPTABLE)

    def get(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        if schema_name == 'public':
            user_s = request.user
            # get schema name
            try:
                check_user_teanant = user_s.tenant_user
            except:
                check_user_teanant = None

            if check_user_teanant or check_user_teanant is not None:
                # check subscription plan
                try:
                    tenant_sub_plan = check_user_teanant.teant_subscriptions
                except:
                    tenant_sub_plan = None

                if tenant_sub_plan:
                    if tenant_sub_plan.date_billing_end - timezone.now() >= timedelta(days=0, hours=0, minutes=0,
                                                                                      seconds=0):
                        validity_time = tenant_sub_plan.date_billing_end - timezone.now()
                        return Response({'message': 'You Already have plan', 'subscription_plane':tenant_sub_plan.subscription.plan.plan_name,
                                         'validity_time':str(validity_time)
                                         }, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'You have no active plan'}, status = status.HTTP_402_PAYMENT_REQUIRED)


class TenantTemplateView(viewsets.ModelViewSet):
    """
    Tenant owner can use template for their websites
    """
    serializer_class = TenantTemplateSerializer
    queryset = TenantTemplate.objects.all().order_by('id')
    permission_classes = (permissions.IsAuthenticated,)


    def get_queryset(self):
        schema_name = connection.schema_name
        if schema_name == 'public':
            user_calling = self.request.user
            if user_calling or user_calling is not None:
                try:
                    check_user_teanant = user_calling.tenant_user
                except:
                    check_user_teanant = None

                if check_user_teanant:
                    return TenantTemplate.objects.filter(teant_attched=check_user_teanant)
                else:
                    return Response({'message': 'User have no tenant'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({'message': 'Not Allowed this request'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def perform_create(self, serializer):
        schema_name = connection.schema_name
        if schema_name == 'public':
            user_calling = self.request.user
            if user_calling or user_calling is not None:
                try:
                    check_user_teanant = user_calling.tenant_user
                except:
                    check_user_teanant = None

                if check_user_teanant:
                    count = TenantTemplate.objects.filter(teant_attched=check_user_teanant).count()
                    if count >= 1:
                        raise ValidationError({'error':"Not Allowed"})
                    serializer.is_valid(raise_exception=True)
                    serializer.save(teant_attched=check_user_teanant)

                else:
                    return Response({'message': 'User have no tenant'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({'message': 'Not Allowed this request'}, status=status.HTTP_406_NOT_ACCEPTABLE)


    def update(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        if schema_name == 'public':
            partial = kwargs.pop('partial', True)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response({'message': 'Not Allowed this request'}, status=status.HTTP_406_NOT_ACCEPTABLE)


    def destroy(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        if schema_name == 'public':
            tenant_template_obj = TenantTemplate.objects.get(pk=self.kwargs['pk'])
            tenant_template_obj.delete()
            return Response({'message': 'deleted'})


class tenatotpView(viewsets.ModelViewSet):
    """
    Tenant owner can use OTP for their websites
    """
    serializer_class = OtpWalletSerializer
    queryset = OtpWallet.objects.all().order_by('id')
    permission_classes = (permissions.IsAuthenticated,)


    def get_queryset(self):
        schema_name = connection.schema_name
        if schema_name == 'public':
            user_calling = self.request.user
            if user_calling or user_calling is not None:
                try:
                    check_user_teanant = user_calling.tenant_user
                except:
                    check_user_teanant = None

                if check_user_teanant:
                    return OtpWallet.objects.filter(teant_attched=check_user_teanant)
                else:
                    return Response({'message': 'User have no tenant'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({'message': 'Not Allowed this request'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def perform_create(self, serializer):
        schema_name = connection.schema_name
        if schema_name == 'public':
            user_calling = self.request.user
            if user_calling or user_calling is not None:
                try:
                    check_user_teanant = user_calling.tenant_user
                except:
                    check_user_teanant = None

                if check_user_teanant:
                    count = OtpWallet.objects.filter(teant_attched=check_user_teanant).count()
                    if count >= 1:
                        raise ValidationError({'error':"Not Allowed"})
                    serializer.is_valid(raise_exception=True)
                    serializer.save(teant_attched=check_user_teanant, user=user_calling)

                else:
                    return Response({'message': 'User have no tenant'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({'message': 'Not Allowed this request'}, status=status.HTTP_406_NOT_ACCEPTABLE)


    def update(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        if schema_name == 'public':
            partial = kwargs.pop('partial', True)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response({'message': 'Not Allowed this request'}, status=status.HTTP_406_NOT_ACCEPTABLE)


    def destroy(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        if schema_name == 'public':
            tenant_template_obj = OtpWallet.objects.get(pk=self.kwargs['pk'])
            tenant_template_obj.delete()
            return Response({'message': 'deleted'})


