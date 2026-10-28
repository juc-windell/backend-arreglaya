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

#====================================================================================
    # Regla 1: el tecnico debe estar activo y su especialidad debe coincidir
    # con la categoria de la solicitud (o ser GENERAL)
    def puede_atender(self, categoria):
        return self.activo and self.especialidad in (categoria, 'GENERAL')

    # Cantidad de ordenes que el tecnico tiene sin finalizar
    # Usa el related_name='ordenes' del campo tecnico en el modelo Orden
    def carga_abierta(self):
        return self.ordenes.exclude(estado='FINALIZADA').count()

    # Regla 2: el tecnico no supera max_ordenes_abiertas
    def tiene_cupo(self):
        return self.carga_abierta() < self.max_ordenes_abiertas