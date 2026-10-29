from django.db.models import Case, Count, IntegerField, ProtectedError, Value, When
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.permisos import OperadorGestiona
from .models import Solicitud
from .serializers import SolicitudSerializer

#==================================================================================
# Peso de la prioridad para poder ordenar (BAJA es la menos urgente)
PESO_PRIORIDAD = Case(
    When(prioridad='BAJA', then=Value(1)),
    When(prioridad='MEDIA', then=Value(2)),
    When(prioridad='ALTA', then=Value(3)),
    When(prioridad='URGENTE', then=Value(4)),
    output_field=IntegerField(),
)

ORDENAMIENTOS = ('fecha_reporte', '-fecha_reporte', 'prioridad', '-prioridad')


class SolicitudViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudSerializer
    permission_classes = [OperadorGestiona]

#==================================================================================
    # Filtros (solo en el listado): ?estado= ?prioridad= ?categoria= ?espacio=
    # Orden: ?ordering=fecha_reporte | -fecha_reporte | prioridad | -prioridad
    # Por defecto: las mas recientes primero
    def get_queryset(self):
        solicitudes = Solicitud.objects.select_related(
            'espacio__edificio', 'reportado_por'
        )

        if self.action != 'list':
            return solicitudes.order_by('id')

        parametros = self.request.query_params

        estado = parametros.get('estado')
        if estado:
            solicitudes = solicitudes.filter(estado=estado.upper())

        prioridad = parametros.get('prioridad')
        if prioridad:
            solicitudes = solicitudes.filter(prioridad=prioridad.upper())

        categoria = parametros.get('categoria')
        if categoria:
            solicitudes = solicitudes.filter(categoria=categoria.upper())

        espacio = parametros.get('espacio')
        if espacio:
            if not espacio.isdigit():
                raise ValidationError({'espacio': 'Use el id numerico del espacio.'})
            solicitudes = solicitudes.filter(espacio_id=espacio)

        orden = parametros.get('ordering', '-fecha_reporte')
        if orden not in ORDENAMIENTOS:
            raise ValidationError(
                {'ordering': 'Use fecha_reporte, -fecha_reporte, prioridad o -prioridad.'}
            )

        if 'prioridad' in orden:
            signo = '-' if orden.startswith('-') else ''
            return solicitudes.annotate(peso=PESO_PRIORIDAD).order_by(
                signo + 'peso', '-fecha_reporte', '-id'
            )

        desempate = '-id' if orden.startswith('-') else 'id'
        return solicitudes.order_by(orden, desempate)

#==================================================================================
    # El usuario del token es quien reporta, no lo envia el cliente
    def perform_create(self, serializer):
        serializer.save(reportado_por=self.request.user)

    # Una solicitud con orden de trabajo no se elimina
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'error': 'No se puede eliminar la solicitud porque tiene una orden de trabajo asociada'},
                status=status.HTTP_409_CONFLICT
            )

#==================================================================================
# Reporte: cantidad de solicitudes por edificio y por estado
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def solicitudes_por_edificio(request):
    filas = (
        Solicitud.objects
        .values('espacio__edificio__nombre', 'estado')
        .annotate(total=Count('id'))
        .order_by('espacio__edificio__nombre', 'estado')
    )

    edificios = {}
    for fila in filas:
        nombre = fila['espacio__edificio__nombre']
        edificio = edificios.setdefault(
            nombre, {'edificio': nombre, 'total': 0, 'por_estado': {}}
        )
        edificio['por_estado'][fila['estado']] = fila['total']
        edificio['total'] += fila['total']

    return Response(list(edificios.values()))
