from django.urls import path
from django.urls.conf import include

from .views import PartViewset, upload_csv

urlpatterns = [
    path('api/parts/', PartViewset.as_view(), name='api-parts'),
    path('import/', upload_csv, name='import'),
    path('celery_progress/', include('celery_progress.urls')),
]