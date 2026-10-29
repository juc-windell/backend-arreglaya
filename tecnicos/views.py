from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, ProtectedError 
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, authentication_classes, permission_classes,)
from usuarios.permisos import SoloAdministradorModifica
from .models import Tecnico
from .serializers import TecnicoSerializer

#=============================================================================
# API Tecnicos
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([SoloAdministradorModifica])
def api_tecnicos(request):
    if request.method == 'GET':
        tecnicos = Tecnico.objects.all().order_by('id')

        # Filtros: ?especialidad=PLOMERIA y ?activo=true
        especialidad = request.query_params.get('especialidad')
        if especialidad:
            tecnicos = tecnicos.filter(especialidad=especialidad.upper())

        activo = request.query_params.get('activo')
        if activo is not None:
            if activo.lower() in ('true', '1'):
                tecnicos = tecnicos.filter(activo=True)
            elif activo.lower() in ('false', '0'):
                tecnicos = tecnicos.filter(activo=False)
            else:
                return Response(
                    {'activo': 'Use true o false'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = TecnicoSerializer(tecnicos, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = TecnicoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

#==================================================================================
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([SoloAdministradorModifica])
def detalle_tecnico(request, pk):
    try:
        tecnico = Tecnico.objects.get(pk=pk)
    except Tecnico.DoesNotExist:
        return Response(
            {'error': 'Tecnico no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = TecnicoSerializer(tecnico)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        serializer = TecnicoSerializer(
            tecnico,
            data=request.data,
            partial=(request.method == 'PATCH')
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'DELETE':
        # No se elimina un tecnico que tiene ordenes de trabajo
        try:
            tecnico.delete()
        except ProtectedError:
            return Response(
                {'error': 'No se puede eliminar el tecnico porque tiene ordenes de trabajo asociadas'},
                status=status.HTTP_409_CONFLICT
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

#==================================================================================
# Reporte: tiempo promedio de resolucion por tecnico (solo ordenes finalizadas)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def tiempo_por_tecnico(request):
    duracion = ExpressionWrapper(
        F('ordenes__fecha_cierre') - F('ordenes__fecha_asignacion'),
        output_field=DurationField()
    )
    tecnicos = (
        Tecnico.objects
        .filter(ordenes__estado='FINALIZADA', ordenes__fecha_cierre__isnull=False)
        .annotate(promedio=Avg(duracion), total_ordenes=Count('ordenes'))
        .order_by('nombre')
    )

    resultado = []
    for tecnico in tecnicos:
        resultado.append({
            'tecnico_id': tecnico.id,
            'tecnico': tecnico.nombre,
            'ordenes_finalizadas': tecnico.total_ordenes,
            'dias_promedio': round(tecnico.promedio.total_seconds() / 86400, 2),
        })
    return Response(resultado)