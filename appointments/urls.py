from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='list'),
    path('add/', views.appointment_add, name='add'),
    path('<int:pk>/edit/', views.appointment_edit, name='edit'),
    path('<int:pk>/delete/', views.appointment_delete, name='delete'),
    path('<int:pk>/status/<str:status>/', views.appointment_update_status, name='update_status'),
]