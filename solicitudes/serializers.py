from rest_framework import serializers
from rest_framework.exceptions import APIException
from .models import Solicitud

#==================================================================================
# la operacion choca con el estado actual de la solicitud
# La respuesta usa la misma forma que el resto de la API: {"error": "mensaje"}
class ConflictoEstado(APIException):
    status_code = 409
    default_detail = 'La operacion entra en conflicto con el estado actual.'
    default_code = 'conflicto'

    def __init__(self, mensaje):
        super().__init__({'error': mensaje})

#==================================================================================
class SolicitudSerializer(serializers.ModelSerializer):
    espacio_nombre = serializers.CharField(source='espacio.nombre', read_only=True)
    edificio_nombre = serializers.CharField(source='espacio.edificio.nombre', read_only=True)

    class Meta:
        model = Solicitud
        fields = [
            'id', 'espacio', 'espacio_nombre', 'edificio_nombre',
            'reportado_por', 'descripcion', 'categoria', 'prioridad',
            'estado', 'fecha_reporte',
        ]
        # reportado_por se llena con request.user en la vista
        read_only_fields = ['reportado_por', 'fecha_reporte']

#==================================================================================
    def validate_descripcion(self, value):
        descripcion = value.strip()

        if len(descripcion) < 5:
            raise serializers.ValidationError(
                'La descripcion debe tener al menos 5 caracteres.'
            )

        return descripcion

#==================================================================================
    # Valida la creacion y la actualizacion (PUT y PATCH)
    def validate(self, attrs):
        # Creacion: una solicitud nueva siempre inicia ABIERTA
        if self.instance is None:
            if attrs.get('estado', 'ABIERTA') != 'ABIERTA':
                raise serializers.ValidationError(
                    {'estado': 'Una solicitud nueva siempre inicia ABIERTA.'}
                )
            return attrs

        solicitud = self.instance
        nuevo = attrs.get('estado', solicitud.estado)
        orden = getattr(solicitud, 'orden', None)

        # RESUELTA y CANCELADA son estados finales: no se modifican
        if solicitud.esta_cerrada():
            raise ConflictoEstado(
                'La solicitud esta ' + solicitud.estado + ' y no se puede modificar.'
            )

        # Regla 8: solo pasa a RESUELTA si su orden esta FINALIZADA
        if nuevo == 'RESUELTA' and (orden is None or orden.estado != 'FINALIZADA'):
            raise ConflictoEstado(
                'La solicitud solo pasa a RESUELTA cuando su orden de trabajo esta FINALIZADA.'
            )

        if nuevo != solicitud.estado:
            if not solicitud.puede_pasar_a(nuevo):
                raise ConflictoEstado(
                    'No se puede pasar de ' + solicitud.estado + ' a ' + nuevo + '.'
                )

            # ASIGNADA y EN_PROCESO dependen de la orden de trabajo
            if nuevo == 'ASIGNADA' and orden is None:
                raise ConflictoEstado(
                    'La solicitud pasa a ASIGNADA al crear su orden de trabajo.'
                )
            if nuevo == 'EN_PROCESO' and (orden is None or orden.estado != 'EN_PROCESO'):
                raise ConflictoEstado(
                    'La solicitud pasa a EN_PROCESO cuando su orden de trabajo esta EN_PROCESO.'
                )

        # Con una orden asignada, la categoria no cambia (el tecnico se eligio por ella)
        if orden is not None and attrs.get('categoria', solicitud.categoria) != solicitud.categoria:
            raise ConflictoEstado(
                'La solicitud ya tiene una orden de trabajo y no se puede cambiar su categoria.'
            )

        return attrs
