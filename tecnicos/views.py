from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
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