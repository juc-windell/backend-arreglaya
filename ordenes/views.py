from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import F, Count, Sum, Q
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from usuarios.permisos import OperadorGestiona
from materiales.models import Material
from solicitudes.models import Solicitud
from tecnicos.models import Tecnico

from .models import Orden, OrdenMaterial
from .serializers import OrdenSerializer, OrdenMaterialSerializer


class Conflicto(Exception):
    pass


class OrdenViewSet(viewsets.ModelViewSet):

    serializer_class = OrdenSerializer
    permission_classes = [OperadorGestiona]

    # Filtros: ?estado=EN_PROCESO y ?tecnico=1
    def get_queryset(self):
        ordenes = Orden.objects.select_related(
            "solicitud", "tecnico"
        ).order_by("id")

        estado = self.request.query_params.get("estado")
        if estado:
            ordenes = ordenes.filter(estado=estado.upper())

        tecnico = self.request.query_params.get("tecnico")
        if tecnico and tecnico.isdigit():
            ordenes = ordenes.filter(tecnico_id=tecnico)

        return ordenes 

    # Crear orden: reglas 1, 2 y 3
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            with transaction.atomic():
                solicitud = Solicitud.objects.select_for_update().get(
                    pk=data["solicitud"].pk
                )
                tecnico = Tecnico.objects.select_for_update().get(
                    pk=data["tecnico"].pk
                )

                if (
                    not solicitud.puede_recibir_orden()
                    or Orden.objects.filter(solicitud=solicitud).exists()
                ):
                    raise Conflicto(
                        "La solicitud no puede recibir una orden."
                    )

                if not tecnico.puede_atender(solicitud.categoria):
                    raise Conflicto(
                        "Tecnico inactivo o especialidad incompatible."
                    )

                if not tecnico.tiene_cupo():
                    raise Conflicto(
                        "El tecnico supero su maximo de ordenes abiertas."
                    )

                if data.get("estado", "ASIGNADA") != "ASIGNADA":
                    raise Conflicto(
                        "Una orden nueva debe iniciar ASIGNADA."
                    )

                orden = Orden(**data)
                orden.full_clean()
                orden.save()

                solicitud.cambiar_estado("ASIGNADA")

        except Conflicto as e:
            return Response({"error": str(e)}, status=409)

        except DjangoValidationError as e:
            return Response(
                {"error": e.message_dict if hasattr(e, "message_dict") else e.messages},
                status=400
            )

        return Response(self.get_serializer(orden).data, status=201)

    # Actualizar orden: reglas 4 y 7
    # Tambien se aplica cuando se usa PATCH
    def update(self, request, *args, **kwargs):
        partial = kwargs.get("partial", False)

        try:
            with transaction.atomic():
                orden = Orden.objects.select_for_update().get(
                    pk=kwargs["pk"]
                )

                if orden.estado == "FINALIZADA":
                    raise Conflicto(
                        "Una orden FINALIZADA no se puede editar."
                    )

                serializer = self.get_serializer(
                    orden, data=request.data, partial=partial
                )
                serializer.is_valid(raise_exception=True)
                data = serializer.validated_data

                if (
                    "solicitud" in data
                    and data["solicitud"].pk != orden.solicitud_id
                ):
                    raise Conflicto(
                        "No se puede cambiar la solicitud de una orden."
                    )

                if (
                    "tecnico" in data
                    and data["tecnico"].pk != orden.tecnico_id
                ):
                    tecnico = Tecnico.objects.select_for_update().get(
                        pk=data["tecnico"].pk
                    )

                    if (
                        not tecnico.puede_atender(orden.solicitud.categoria)
                        or not tecnico.tiene_cupo()
                    ):
                        raise Conflicto(
                            "Tecnico incompatible, inactivo o sin cupo."
                        )

                nuevo_estado = data.get("estado", orden.estado)

                if nuevo_estado not in (
                    orden.estado, "EN_PROCESO", "FINALIZADA"
                ):
                    raise Conflicto("Transicion de estado invalida.")

                if (
                    orden.estado == "ASIGNADA"
                    and nuevo_estado == "FINALIZADA"
                ):
                    raise Conflicto(
                        "La orden debe estar EN_PROCESO antes de finalizar."
                    )

                # Si la solicitud ya no se puede resolver (por ejemplo, fue
                # cancelada), no se finaliza la orden
                if (
                    nuevo_estado == "FINALIZADA"
                    and orden.estado != "FINALIZADA"
                    and not orden.solicitud.puede_pasar_a("RESUELTA")
                ):
                    raise Conflicto(
                        "La solicitud no se puede resolver en su estado actual."
                    )
                    
                for field, value in data.items():
                    setattr(orden, field, value)

                if (
                    nuevo_estado == "FINALIZADA"
                    and orden.fecha_cierre is None
                ):
                    orden.fecha_cierre = timezone.now()

                if (
                    nuevo_estado != "FINALIZADA"
                    and orden.fecha_cierre is not None
                ):
                    raise Conflicto(
                        "fecha_cierre solo corresponde a una orden FINALIZADA."
                    )

                orden.full_clean()
                orden.save()

                if (
                    nuevo_estado == "EN_PROCESO"
                    and orden.solicitud.estado == "ASIGNADA"
                ):
                    orden.solicitud.cambiar_estado("EN_PROCESO")

                if nuevo_estado == "FINALIZADA":
                    orden.solicitud.cambiar_estado("RESUELTA")

        except Orden.DoesNotExist:
            return Response({"error": "Orden no encontrada"}, status=404)

        except Conflicto as e:
            return Response({"error": str(e)}, status=409)

        except DjangoValidationError as e:
            return Response(
                {"error": e.message_dict if hasattr(e, "message_dict") else e.messages},
                status=400
            )

        return Response(self.get_serializer(orden).data)

    # Conservar historial
    def destroy(self, request, *args, **kwargs):
        return Response(
            {"error": "Las ordenes se conservan como historial."},
            status=409
        )

    # Registrar materiales: reglas 5, 6 y 7
    @action(detail=True, methods=["get", "post"], url_path="materiales")
    def materiales(self, request, pk=None):

        if request.method == "GET":
            orden = self.get_object()
            detalles = orden.detalles_materiales.all()

            return Response(
                OrdenMaterialSerializer(detalles, many=True).data
            )

        if not (
            request.user.is_superuser
            or request.user.groups.filter(
                name__in=["Administrador", "Operador"]
            ).exists()
        ):
            return Response({"error": "Sin permiso"}, status=403)

        try:
            material_id = int(request.data.get("material"))
            cantidad = int(request.data.get("cantidad"))
        except (TypeError, ValueError):
            return Response(
                {"error": "material y cantidad deben ser enteros."},
                status=400
            )

        if cantidad <= 0:
            return Response(
                {"error": "Cantidad debe ser mayor que cero."},
                status=400
            )

        try:
            with transaction.atomic():
                orden = Orden.objects.select_for_update().get(pk=pk)

                if orden.estado == "FINALIZADA":
                    raise Conflicto(
                        "Una orden FINALIZADA no admite materiales."
                    )

                material = Material.objects.select_for_update().get(
                    pk=material_id
                )

                if not material.activo:
                    raise Conflicto(
                        "No se pueden utilizar materiales inactivos."
                    )

                if material.stock_actual < cantidad:
                    raise Conflicto("Stock insuficiente.")

                detalle, creado = OrdenMaterial.objects.get_or_create(
                    orden=orden,
                    material=material,
                    defaults={"cantidad": cantidad}
                )

                if not creado:
                    detalle.cantidad += cantidad
                    detalle.save(update_fields=["cantidad"])

                Material.objects.filter(pk=material.pk).update(
                    stock_actual=F("stock_actual") - cantidad
                )

        except Orden.DoesNotExist:
            return Response({"error": "Orden no encontrada"}, status=404)

        except Material.DoesNotExist:
            return Response({"error": "Material no encontrado"}, status=404)

        except Conflicto as e:
            return Response({"error": str(e)}, status=409)

        return Response(
            OrdenMaterialSerializer(detalle).data,
            status=201
        )

    # Tres consultas ORM de Persona B
    @action(detail=False, methods=["get"], url_path="consultas")
    def consultas(self, request):

        # Consulta 1: ordenes abiertas por tecnico
        carga = list(
            Tecnico.objects.annotate(
                ordenes_abiertas=Count(
                    "ordenes",
                    filter=~Q(ordenes__estado="FINALIZADA")
                )
            ).values("id", "nombre", "ordenes_abiertas")
        )

        # Consulta 2: consumo total por material
        consumo = list(
            Material.objects.annotate(
                total_utilizado=Sum("usos__cantidad")
            ).values("id", "nombre", "total_utilizado")
        )

        # Consulta 3: cantidad de ordenes por estado
        estados = list(
            Orden.objects.values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )

        # Consulta 4: materiales por debajo del stock minimo
        bajo_stock = list(
            Material.objects.filter(
                stock_actual__lt=F("stock_minimo")
            ).values("id", "codigo", "nombre", "stock_actual", "stock_minimo")
        )

        return Response({
            "carga_tecnicos": carga,
            "consumo_materiales": consumo,
            "ordenes_por_estado": estados,
            "bajo_stock": bajo_stock
        })

