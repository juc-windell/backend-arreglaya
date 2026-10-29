from django.conf import settings
from django.db import models
from espacios.models import Espacio
from tecnicos.models import Tecnico

class Solicitud(models.Model):
    # La categoria usa la misma lista que la especialidad del tecnico
    CATEGORIAS = Tecnico.ESPECIALIDADES

    PRIORIDADES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]

    ESTADOS = [
        ('ABIERTA', 'Abierta'),
        ('ASIGNADA', 'Asignada'),
        ('EN_PROCESO', 'En proceso'),
        ('RESUELTA', 'Resuelta'),
        ('CANCELADA', 'Cancelada'),
    ]

    # Estados a los que se puede pasar desde cada estado
    TRANSICIONES = {
        'ABIERTA': ['ASIGNADA', 'CANCELADA'],
        'ASIGNADA': ['EN_PROCESO', 'CANCELADA'],
        'EN_PROCESO': ['RESUELTA', 'CANCELADA'],
        'RESUELTA': [],
        'CANCELADA': [],
    }

    espacio = models.ForeignKey(
        Espacio,
        on_delete=models.PROTECT,
        related_name='solicitudes'
    )
    # Se llena con request.user, no lo envia el cliente
    reportado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='solicitudes_reportadas'
    )
    descripcion = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='MEDIA')
    estado = models.CharField(max_length=15, choices=ESTADOS, default='ABIERTA')
    fecha_reporte = models.DateTimeField(auto_now_add=True)

#=========================================================================================
    # RESUELTA y CANCELADA son estados finales
    def esta_cerrada(self):
        return self.estado in ('RESUELTA', 'CANCELADA')

    # Regla 3: solo una solicitud ABIERTA recibe una orden nueva.
    # Una ASIGNADA ya tiene orden y una RESUELTA o CANCELADA esta cerrada
    def puede_recibir_orden(self):
        return self.estado == 'ABIERTA'

    def puede_pasar_a(self, nuevo_estado):
        return nuevo_estado in self.TRANSICIONES[self.estado]

    # Cambia el estado si la transicion es valida; si no, lanza ValueError
    # (la vista que lo llame lo convierte en una respuesta 409)
    def cambiar_estado(self, nuevo_estado):
        if not self.puede_pasar_a(nuevo_estado):
            raise ValueError(
                'No se puede pasar de ' + self.estado + ' a ' + nuevo_estado
            )
        self.estado = nuevo_estado
        self.save(update_fields=['estado'])

    def __str__(self):
        return 'Solicitud ' + str(self.id) + ' - ' + self.espacio.nombre
