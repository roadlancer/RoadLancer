from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # API App Endpoints (will be populated in Phase 1 & 2)
    # path('api/auth/', include('apps.accounts.urls')),
    # path('api/shipments/', include('apps.shipments.urls')),
]
