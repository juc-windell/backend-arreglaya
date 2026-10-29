from rest_framework.routers import SimpleRouter
from .views import OrdenViewSet

router = SimpleRouter()

router.register(
    "api/ordenes",
    OrdenViewSet,
    basename="ordenes"
)

urlpatterns = router.urls