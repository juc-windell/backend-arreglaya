from rest_framework.routers import SimpleRouter
from .views import MaterialViewSet

router = SimpleRouter()

router.register(
    "api/materiales",
    MaterialViewSet,
    basename="materiales"
)

urlpatterns = router.urls