from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet

router = DefaultRouter()

router.register(
    "api/materiales",
    MaterialViewSet,
    basename="materiales"
)

urlpatterns = router.urls