from rest_framework import serializers
from .models import Tecnico

#============================================================================
class TecnicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tecnico
        fields = '__all__'

    def validate_nombre(self, value):
        nombre_limpio = value.strip()

        if len(nombre_limpio) < 3:
            raise serializers.ValidationError(
                'El nombre debe tener al menos 3 caracteres'
            )
        return nombre_limpio

    def validate_identificacion(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                'La identificacion solo puede tener numeros'
            )
        return value

    def validate_telefono(self, value):
        if not value.isdigit() or len(value) != 8:
            raise serializers.ValidationError(
                'El telefono debe tener 8 digitos.'
            )
        return value

    def validate_max_ordenes_abiertas(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'El maximo de ordenes abiertas debe ser al menos 1'
            )
        return value