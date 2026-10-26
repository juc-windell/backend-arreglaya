from rest_framework.permissions import BasePermission, SAFE_METHODS

#===================================================================================
# Nombres de los grupos del sistema
ADMINISTRADOR = 'Administrador'
OPERADOR = 'Operador'
CONSULTA = 'Consulta'

def es_administrador(usuario):
    return (
        usuario.is_superuser
        or usuario.groups.filter(name=ADMINISTRADOR).exists()
    )

def es_operador(usuario):
    return usuario.groups.filter(name=OPERADOR).exists()

#==================================================================================
# Para espacios, tecnicos y materiales
class SoloAdministradorModifica(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return es_administrador(request.user)
    
#==================================================================================
# Para solicitudes y ordenes de trabajo:
class OperadorGestiona(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.method == 'DELETE':
            return es_administrador(request.user)

        return es_administrador(request.user) or es_operador(request.user)