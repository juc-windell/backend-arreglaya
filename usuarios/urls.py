from django.urls import path
from . import views

#===================================================================
urlpatterns = [
    path('api/perfil/', views.perfil, name='api_perfil'),
]