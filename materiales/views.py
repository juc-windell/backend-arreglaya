from django.db.models import ProtectedError, Q
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from usuarios.permisos import SoloAdministradorModifica
from .models import Material
from .serializers import MaterialSerializer


class MaterialViewSet(viewsets.ModelViewSet):
    serializer_class = MaterialSerializer
    permission_classes = [SoloAdministradorModifica]

    # Filtros: ?activo=true y ?search=cable (busca en nombre y codigo)
    def get_queryset(self):
        materiales = Material.objects.all().order_by("id")

        activo = self.request.query_params.get("activo")
        if activo is not None:
            if activo.lower() in ("true", "1"):
                materiales = materiales.filter(activo=True)
            elif activo.lower() in ("false", "0"):
                materiales = materiales.filter(activo=False)
            else:
                raise ValidationError({"activo": "Use true o false."})

        buscar = self.request.query_params.get("search")
        if buscar:
            materiales = materiales.filter(
                Q(nombre__icontains=buscar) | Q(codigo__icontains=buscar)
            )

        return materiales

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"error": "Material con registros asociados."},
                status=status.HTTP_409_CONFLICT
            )