from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from accounts.views import home_view

def health_check(request):
    return JsonResponse({'status': 'healthy', 'app': 'LoveMatch', 'version': '2.0.0'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('health/', health_check, name='health_check'),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('matching/', include('matching.urls')),
    path('chat/', include('chat.urls')),
    path('webpush/', include('webpush.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
