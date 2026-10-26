from django.db import models

#=============================================================================
class Edificio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=10)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
#==============================================================================
class Espacio(models.Model):
    TIPOS = [
        ('AULA', 'Aula'),
        ('LABORATORIO', 'Laboratorio'),
        ('OFICINA', 'Oficina'),
        ('BAÑO', 'Baño'),
        ('EXTERIOR', 'Exterior'),
    ]

    # PROTECT no deja borrar un edificio que tenga espacios
    edificio = models.ForeignKey(Edificio,on_delete=models.PROTECT,related_name='espacios')
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    piso = models.IntegerField()
    
#==================================================================================
    class Meta:
        # No se repite el nombre de un espacio dentro del mismo edificio
        constraints = [
            models.UniqueConstraint(
                fields=['edificio', 'nombre'],
                name='espacio_unico_por_edificio'
            )
        ]

    def __str__(self):
        return self.edificio.nombre + ' - ' + self.nombre