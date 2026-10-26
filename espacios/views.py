from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (api_view, authentication_classes, permission_classes,)
from usuarios.permisos import SoloAdministradorModifica
from .models import Edificio, Espacio
from .serializers import EdificioSerializer, EspacioSerializer

#==================================================================================
# API de Edificio
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([SoloAdministradorModifica])
def api_edificios(request):
    if request.method == 'GET':
        edificios = Edificio.objects.all().order_by('id')
        serializer = EdificioSerializer(edificios, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = EdificioSerializer(data=request.data)

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
def detalle_edificio(request, pk):
    try:
        edificio = Edificio.objects.get(pk=pk)
    except Edificio.DoesNotExist:
        return Response(
            {'error': 'Edificio no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = EdificioSerializer(edificio)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        serializer = EdificioSerializer(
            edificio,
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
        # No se elimina un edificio que tiene espacios 
        try:
            edificio.delete()
        except ProtectedError:
            return Response(
                {'error': 'No se puede eliminar el edificio porque tiene espacios asociados'},
                status=status.HTTP_409_CONFLICT
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

#=============================================================================================
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([SoloAdministradorModifica])
def api_espacios(request):
    if request.method == 'GET':
        espacios = Espacio.objects.all().order_by('id')
        serializer = EspacioSerializer(espacios, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = EspacioSerializer(data=request.data)

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

#=============================================================================================
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([SoloAdministradorModifica])
def detalle_espacio(request, pk):
    try:
        espacio = Espacio.objects.get(pk=pk)
    except Espacio.DoesNotExist:
        return Response(
            {'error': 'Espacio no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = EspacioSerializer(espacio)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        serializer = EspacioSerializer(
            espacio,
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
        # No se elimina un espacio que tiene solicitudes
        try:
            espacio.delete()
        except ProtectedError:
            return Response(
                {'error': 'No se puede eliminar el espacio porque tiene solicitudes asociadas'},
                status=status.HTTP_409_CONFLICT
            )
        return Response(status=status.HTTP_204_NO_CONTENT)