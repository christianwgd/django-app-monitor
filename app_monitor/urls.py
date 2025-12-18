"""
URL configuration for django_app_monitor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    # 1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView


admin.autodiscover()
admin.site.site_header = _('Django App Monitor')
admin.site.login = secure_admin_login(admin.site.login)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/signup/', RedirectView.as_view(url='/', permanent=True)),
    path('accounts/', include('allauth.urls')),
    path('app/', include('app.urls')),
    path('', RedirectView.as_view(pattern_name='app:list', permanent=False), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
