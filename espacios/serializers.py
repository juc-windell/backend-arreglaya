from rest_framework import serializers
from .models import Edificio, Espacio

#==================================================================================
class EdificioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edificio
        fields = '__all__'

    def validate_nombre(self, value):
        nombre_limpio = value.strip()

        if len(nombre_limpio) < 3:
            raise serializers.ValidationError(
                'El nombre debe tener al menos 3 caracteres'
            )
        return nombre_limpio

    def validate_codigo(self, value):
        codigo_limpio = value.strip().upper()

        if len(codigo_limpio) < 2:
            raise serializers.ValidationError(
                'El codigo debe tener al menos 2 caracteres'
            )
        return codigo_limpio

#===========================================================================================
class EspacioSerializer(serializers.ModelSerializer):
    # Proyecto 2: nombre del edificio (solo lectura) para mostrar la relacion
    # en el listado del frontend sin una consulta extra por cada fila
    edificio_nombre = serializers.CharField(source='edificio.nombre', read_only=True)

    class Meta:
        model = Espacio
        fields = '__all__'

    def validate_nombre(self, value):
        nombre_limpio = value.strip()

        if len(nombre_limpio) < 3:
            raise serializers.ValidationError(
                'El nombre debe tener al menos 3 caracteres'
            )
        return nombre_limpio

    def validate_piso(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'El piso no puede ser negativo'
            )
        return value
