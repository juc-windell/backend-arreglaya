from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (api_view, authentication_classes, permission_classes,)
from rest_framework.permissions import IsAuthenticated

#===========================================================================
# Devuelve los datos del usuario que envia el token y sus grupos
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def perfil(request):
    grupos = []
    for grupo in request.user.groups.all():
        grupos.append(grupo.name)

    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email,
        "grupos": grupos,
    })