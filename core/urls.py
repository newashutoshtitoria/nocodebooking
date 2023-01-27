from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt import views as jwt_views
from .tenantspecifictoken import MyTokenObtainPairView
from rest_framework.routers import DefaultRouter
from tenant.views import TenantTemplateView, tenatotpView, Home



router = DefaultRouter()
router.register(r'tenanttemplate', TenantTemplateView)
router.register(r'tenatotp', tenatotpView)


urlpatterns = [
    re_path(r'apis/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('appuser/', include('users.appurl')),
    path('usersapp/', include('users.urls')),
    path('company/', include('tenant.urls')),
    path('firsttenant/', include('main.urls')),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r"^.*/$", Home.as_view(), name='home'),
    re_path(r"^$", Home.as_view(), name='home'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

