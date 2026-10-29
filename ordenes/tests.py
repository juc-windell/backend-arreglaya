from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from espacios.models import Edificio, Espacio
from materiales.models import Material
from solicitudes.models import Solicitud
from tecnicos.models import Tecnico
from .models import Orden

#=========================================================================================
class OrdenesAPITest(APITestCase):
    def setUp(self):
        Usuario = get_user_model()

        self.operador = Usuario.objects.create_user(
            username='operador_prueba', password='ClaveSegura123!')
        self.operador.groups.add(Group.objects.create(name='Operador'))

        self.consulta = Usuario.objects.create_user(
            username='consulta_prueba', password='ClaveSegura123!')
        self.consulta.groups.add(Group.objects.create(name='Consulta'))

        edificio = Edificio.objects.create(nombre='Edificio A', codigo='EA')
        self.espacio = Espacio.objects.create(
            edificio=edificio, nombre='Aula 101', tipo='AULA', piso=1)

        self.tecnico = Tecnico.objects.create(
            nombre='Carlos Mora', identificacion='101110111',
            especialidad='ELECTRICIDAD', telefono='88881111',
            max_ordenes_abiertas=1)

        self.material = Material.objects.create(
            codigo='CAB01', nombre='Cable', stock_actual=10)

        self.client.force_authenticate(user=self.operador)

    def crear_solicitud(self, categoria='ELECTRICIDAD'):
        return Solicitud.objects.create(
            espacio=self.espacio, reportado_por=self.operador,
            descripcion='Falla', categoria=categoria)

    def crear_orden(self, solicitud):
        return self.client.post('/api/ordenes/', {
            'solicitud': solicitud.id,
            'tecnico': self.tecnico.id,
        })

#=========================================================================================
    # CRUD: crear una orden, la solicitud pasa a ASIGNADA y se puede consultar
    def test_crea_orden_y_asigna_solicitud(self):
        solicitud = self.crear_solicitud()
        response = self.crear_orden(solicitud)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'ASIGNADA')

        response = self.client.get('/api/ordenes/' + str(response.data['id']) + '/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

#=========================================================================================
    # Regla 1: la especialidad del tecnico debe coincidir con la categoria
    def test_tecnico_con_otra_especialidad(self):
        response = self.crear_orden(self.crear_solicitud('PLOMERIA'))
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

#=========================================================================================
    # Regla 2: el tecnico no supera su maximo de ordenes abiertas (maximo 1)
    def test_tecnico_sin_cupo(self):
        self.assertEqual(
            self.crear_orden(self.crear_solicitud()).status_code,
            status.HTTP_201_CREATED)
        response = self.crear_orden(self.crear_solicitud())
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

#=========================================================================================
    # Regla 5: el stock no puede quedar negativo
    def test_stock_insuficiente(self):
        orden_id = self.crear_orden(self.crear_solicitud()).data['id']
        response = self.client.post(
            '/api/ordenes/' + str(orden_id) + '/materiales/',
            {'material': self.material.id, 'cantidad': 99})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.material.refresh_from_db()
        self.assertEqual(self.material.stock_actual, 10)

#=========================================================================================
    # Regla 7: una orden finalizada no se edita, tampoco con PATCH
    def test_orden_finalizada_no_se_edita(self):
        orden_id = self.crear_orden(self.crear_solicitud()).data['id']
        url = '/api/ordenes/' + str(orden_id) + '/'
        self.client.patch(url, {'estado': 'EN_PROCESO'})
        response = self.client.patch(url, {'estado': 'FINALIZADA'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(url, {'observaciones': 'cambio'})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

#=========================================================================================
    # Si la solicitud fue cancelada, la orden no se finaliza 
    def test_no_finaliza_si_solicitud_cancelada(self):
        solicitud = self.crear_solicitud()
        orden_id = self.crear_orden(solicitud).data['id']
        url = '/api/ordenes/' + str(orden_id) + '/'
        self.client.patch(url, {'estado': 'EN_PROCESO'})

        solicitud.refresh_from_db()
        solicitud.cambiar_estado('CANCELADA')

        response = self.client.patch(url, {'estado': 'FINALIZADA'})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

#=========================================================================================
    # Permisos: Consulta no crea (403) y sin token responde 401
    def test_permisos(self):
        solicitud = self.crear_solicitud()
        self.client.force_authenticate(user=self.consulta)
        self.assertEqual(self.crear_orden(solicitud).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get('/api/ordenes/').status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get('/api/ordenes/').status_code, status.HTTP_401_UNAUTHORIZED)

#=========================================================================================
    # Filtro por estado y por tecnico
    def test_filtros_de_ordenes(self):
        self.crear_orden(self.crear_solicitud())
        response = self.client.get('/api/ordenes/', {'estado': 'asignada', 'tecnico': self.tecnico.id})
        self.assertEqual(response.data['count'], 1)
        response = self.client.get('/api/ordenes/', {'estado': 'FINALIZADA'})
        self.assertEqual(response.data['count'], 0)
