from django.db.models import ProtectedError
from rest_framework import viewsets, status
from rest_framework.response import Response

from usuarios.permisos import SoloAdministradorModifica
from .models import Material
from .serializers import MaterialSerializer


class MaterialViewSet(viewsets.ModelViewSet):

    queryset = Material.objects.all().order_by("id")
    serializer_class = MaterialSerializer
    permission_classes = [SoloAdministradorModifica]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"error": "Material con registros asociados."},
                status=status.HTTP_409_CONFLICT
            )
