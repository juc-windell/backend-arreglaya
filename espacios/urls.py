from django.urls import path
from . import views

#=====================================================================================
urlpatterns = [
    path('api/edificios/', views.api_edificios, name='api_edificios'),

    path('api/edificios/<int:pk>/', views.detalle_edificio,name='detalle_edificio'),

    path('api/espacios/', views.api_espacios, name='api_espacios'),

    path('api/espacios/<int:pk>/', views.detalle_espacio,name='detalle_espacio'),
]