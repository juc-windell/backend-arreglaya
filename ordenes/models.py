from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Orden(models.Model):

    ESTADOS = [
        ("ASIGNADA", "Asignada"),
        ("EN_PROCESO", "En proceso"),
        ("FINALIZADA", "Finalizada"),
    ]

    solicitud = models.OneToOneField(
        "solicitudes.Solicitud",
        on_delete=models.PROTECT,
        related_name="orden"
    )

    tecnico = models.ForeignKey(
        "tecnicos.Tecnico",
        on_delete=models.PROTECT,
        related_name="ordenes"
    )

    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default="ASIGNADA"
    )

    fecha_asignacion = models.DateTimeField(
        default=timezone.now
    )

    fecha_cierre = models.DateTimeField(
        null=True,
        blank=True
    )

    observaciones = models.TextField(blank=True)

    materiales = models.ManyToManyField(
        "materiales.Material",
        through="OrdenMaterial",
        related_name="ordenes"
    )

    def clean(self):

        if self.estado != "FINALIZADA" and self.fecha_cierre is not None:
            raise ValidationError({
                "fecha_cierre":
                "Solo se permite fecha_cierre en una orden FINALIZADA."
            })

        if (
            self.fecha_cierre
            and self.fecha_asignacion
            and self.fecha_cierre < self.fecha_asignacion
        ):
            raise ValidationError({
                "fecha_cierre":
                "No puede ser anterior a fecha_asignacion."
            })

    def __str__(self):
        return f"Orden {self.pk}"


class OrdenMaterial(models.Model):

    orden = models.ForeignKey(
        Orden,
        on_delete=models.PROTECT,
        related_name="detalles_materiales"
    )

    material = models.ForeignKey(
        "materiales.Material",
        on_delete=models.PROTECT,
        related_name="usos"
    )

    cantidad = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["orden", "material"],
                name="unico_material_por_orden"
            )
        ]
