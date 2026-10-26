from django.db import models

#====================================================================================
class Tecnico(models.Model):
    # Esta misma lista la usa solicitudes para el campo categoria
    ESPECIALIDADES = [
        ('ELECTRICIDAD', 'Electricidad'),
        ('PLOMERIA', 'Plomeria'),
        ('AIRES', 'Aires'),
        ('GENERAL', 'General'),
    ]

    nombre = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=20, choices=ESPECIALIDADES)
    telefono = models.CharField(max_length=15)
    activo = models.BooleanField(default=True)
    max_ordenes_abiertas = models.PositiveIntegerField(default=3)

    def __str__(self):
        return self.nombre