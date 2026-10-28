from rest_framework import serializers
from .models import Orden, OrdenMaterial


class OrdenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Orden
        fields = [
            "id",
            "solicitud",
            "tecnico",
            "estado",
            "fecha_asignacion",
            "fecha_cierre",
            "observaciones"
        ]

        read_only_fields = ["id"]


class OrdenMaterialSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrdenMaterial
        fields = [
            "id",
            "orden",
            "material",
            "cantidad"
        ]

        read_only_fields = ["id", "orden"]

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "La cantidad debe ser positiva."
            )

        return value