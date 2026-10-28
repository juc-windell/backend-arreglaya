from django.urls import path
from . import views

#====================================================================================
urlpatterns = [
    path('api/tecnicos/', views.api_tecnicos, name='api_tecnicos'),

    path('api/tecnicos/<int:pk>/', views.detalle_tecnico,name='detalle_tecnico'),

    path('api/reportes/tiempo-por-tecnico/', views.tiempo_por_tecnico,name='tiempo_por_tecnico'),
]