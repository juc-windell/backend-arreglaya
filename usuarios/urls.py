from django.urls import path
from . import views

#===================================================================
urlpatterns = [
    path('api/perfil/', views.perfil, name='api_perfil'),
    path('api/logout/', views.logout, name='api_logout'),
]
