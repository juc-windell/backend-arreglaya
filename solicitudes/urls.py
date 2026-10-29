from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import SolicitudViewSet, solicitudes_por_edificio

#=====================================================================================
router = SimpleRouter()

router.register(
    'api/solicitudes',
    SolicitudViewSet,
    basename='solicitudes'
)

urlpatterns = [
    path('api/reportes/solicitudes-por-edificio/', solicitudes_por_edificio,
         name='solicitudes_por_edificio'),
] + router.urls
