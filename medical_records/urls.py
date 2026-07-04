from django.urls import path
from . import views

app_name = 'medical_records'

urlpatterns = [
    path('patient/<int:patient_id>/', views.patient_records, name='patient_records'),
    path('upload/', views.upload_record, name='upload_record'),
    path('delete/<int:pk>/', views.delete_record, name='delete_record'),
]