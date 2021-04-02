from django.urls import path
from . import views

urlpatterns = [
    path('parts/', views.PartViewset.as_view()),
    # path('import/', views.upload_csv_from_form, name='csv_import'),
]