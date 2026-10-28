from django.db import models


class Material(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    unidad_medida = models.CharField(max_length=30, default="unidad")
    stock_actual = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
