from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from api import urls as api_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urls)),
]

if settings.DEBUG:
    import debug_toolbar
    
    urlpatterns.extend([
        path('__debug__/', include(debug_toolbar.urls)),
    ])
