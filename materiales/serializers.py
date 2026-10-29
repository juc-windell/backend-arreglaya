from rest_framework import serializers
from .models import Material


class MaterialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Material
        fields = "__all__"

    def validate_codigo(self, value):
        codigo = value.strip().upper()

        if len(codigo) < 2:
            raise serializers.ValidationError(
                "El codigo debe tener al menos 2 caracteres."
            )

        # Se revisa el repetido despues de pasar a mayusculas
        repetidos = Material.objects.filter(codigo=codigo)
        if self.instance:
            repetidos = repetidos.exclude(pk=self.instance.pk)
        if repetidos.exists():
            raise serializers.ValidationError(
                "Ya existe un material con ese codigo."
            )

        return codigo

    def validate_nombre(self, value):
        nombre = value.strip()

        if len(nombre) < 3:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 3 caracteres."
            )

        return nombre