from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.doctor_list, name='list'),
    path('add/', views.doctor_add, name='add'),
    path('<int:pk>/edit/', views.doctor_edit, name='edit'),
    path('<int:pk>/delete/', views.doctor_delete, name='delete'),
]