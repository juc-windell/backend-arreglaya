from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from espacios.models import Edificio, Espacio
from ordenes.models import Orden
from tecnicos.models import Tecnico
from .models import Solicitud

#=========================================================================================
class SolicitudesAPITest(APITestCase):
    def setUp(self):
        Usuario = get_user_model()

        self.admin = Usuario.objects.create_user(
            username='admin_prueba', password='ClaveSegura123!')
        self.admin.groups.add(Group.objects.create(name='Administrador'))

        self.operador = Usuario.objects.create_user(
            username='operador_prueba', password='ClaveSegura123!')
        self.operador.groups.add(Group.objects.create(name='Operador'))

        self.consulta = Usuario.objects.create_user(
            username='consulta_prueba', password='ClaveSegura123!')
        self.consulta.groups.add(Group.objects.create(name='Consulta'))

        self.edificio = Edificio.objects.create(nombre='Edificio A', codigo='EA')
        self.espacio = Espacio.objects.create(
            edificio=self.edificio, nombre='Aula 101', tipo='AULA', piso=1)

        self.tecnico = Tecnico.objects.create(
            nombre='Carlos Mora', identificacion='101110111',
            especialidad='ELECTRICIDAD', telefono='88881111')

        self.client.force_authenticate(user=self.operador)

    def crear(self, **datos):
        valores = {
            'espacio': self.espacio, 'reportado_por': self.operador,
            'descripcion': 'La luz no enciende', 'categoria': 'ELECTRICIDAD',
        }
        valores.update(datos)
        return Solicitud.objects.create(**valores)

    def datos_validos(self, **cambios):
        datos = {
            'espacio': self.espacio.id, 'descripcion': 'La luz no enciende',
            'categoria': 'ELECTRICIDAD', 'prioridad': 'ALTA',
        }
        datos.update(cambios)
        return datos

#=========================================================================================
    # CRUD: crear. reportado_por sale del token y el estado inicial es ABIERTA
    def test_crea_solicitud(self):
        response = self.client.post('/api/solicitudes/', self.datos_validos())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['estado'], 'ABIERTA')
        self.assertEqual(response.data['reportado_por'], self.operador.id)
        self.assertEqual(response.data['edificio_nombre'], 'Edificio A')

    # CRUD: crear con datos invalidos da 400
    def test_crea_solicitud_invalida(self):
        for cambios in ({'descripcion': 'ab'}, {'categoria': 'MAGIA'},
                        {'estado': 'RESUELTA'}, {'espacio': 99999}):
            response = self.client.post('/api/solicitudes/', self.datos_validos(**cambios))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, cambios)

    # CRUD: detalle y 404
    def test_detalle_y_404(self):
        solicitud = self.crear()
        response = self.client.get('/api/solicitudes/' + str(solicitud.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/api/solicitudes/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # CRUD: actualizar con PATCH
    def test_actualiza_con_patch(self):
        solicitud = self.crear()
        response = self.client.patch(
            '/api/solicitudes/' + str(solicitud.id) + '/', {'prioridad': 'URGENTE'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['prioridad'], 'URGENTE')

    # CRUD: eliminar es solo del administrador
    def test_elimina_solo_administrador(self):
        solicitud = self.crear()
        url = '/api/solicitudes/' + str(solicitud.id) + '/'
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_204_NO_CONTENT)

    # PROTECT: una solicitud con orden de trabajo no se elimina (409)
    def test_no_elimina_solicitud_con_orden(self):
        solicitud = self.crear()
        Orden.objects.create(solicitud=solicitud, tecnico=self.tecnico)
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete('/api/solicitudes/' + str(solicitud.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

#=========================================================================================
    # Regla 8: pasa a resuelta solo si su orden esta finalizada
    def test_regla_8_resuelta_exige_orden_finalizada(self):
        solicitud = self.crear()
        url = '/api/solicitudes/' + str(solicitud.id) + '/'

        # Sin orden
        response = self.client.patch(url, {'estado': 'RESUELTA'})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Con la orden en_proceso
        orden = Orden.objects.create(
            solicitud=solicitud, tecnico=self.tecnico, estado='EN_PROCESO')
        solicitud.cambiar_estado('ASIGNADA')
        solicitud.cambiar_estado('EN_PROCESO')
        response = self.client.patch(url, {'estado': 'RESUELTA'})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Con la orden finalizada
        orden.estado = 'FINALIZADA'
        orden.save()
        response = self.client.patch(url, {'estado': 'RESUELTA'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # asignada depende de la orden: no se puede poner a mano
    def test_no_asigna_sin_orden(self):
        solicitud = self.crear()
        response = self.client.patch(
            '/api/solicitudes/' + str(solicitud.id) + '/', {'estado': 'ASIGNADA'})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    # Una solicitud cancelada no se modifica, tampoco con PATCH
    def test_solicitud_cerrada_no_se_edita(self):
        solicitud = self.crear()
        url = '/api/solicitudes/' + str(solicitud.id) + '/'
        self.assertEqual(
            self.client.patch(url, {'estado': 'CANCELADA'}).status_code,
            status.HTTP_200_OK)
        response = self.client.patch(url, {'prioridad': 'BAJA'})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    # Con orden asignada, la categoria no cambia
    def test_no_cambia_categoria_con_orden(self):
        solicitud = self.crear()
        Orden.objects.create(solicitud=solicitud, tecnico=self.tecnico)
        solicitud.cambiar_estado('ASIGNADA')
        response = self.client.patch(
            '/api/solicitudes/' + str(solicitud.id) + '/', {'categoria': 'PLOMERIA'})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

#=========================================================================================
    # Paginacion: 7 solicitudes, la pagina 1 trae 5, la 2 trae 2 y la 99 da 404
    def test_paginacion(self):
        for i in range(7):
            self.crear(descripcion='Falla numero ' + str(i))

        response = self.client.get('/api/solicitudes/')
        self.assertEqual(response.data['count'], 7)
        self.assertEqual(len(response.data['results']), 5)

        response = self.client.get('/api/solicitudes/', {'page': 2})
        self.assertEqual(len(response.data['results']), 2)

        response = self.client.get('/api/solicitudes/', {'page': 99})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Filtro combinado por estado y prioridad
    def test_filtro_combinado(self):
        self.crear(prioridad='ALTA')
        self.crear(prioridad='BAJA')
        self.crear(prioridad='ALTA', estado='CANCELADA')

        response = self.client.get(
            '/api/solicitudes/', {'estado': 'abierta', 'prioridad': 'ALTA'})
        self.assertEqual(response.data['count'], 1)

        response = self.client.get('/api/solicitudes/', {'espacio': 'abc'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Orden: -prioridad deja primero las mas urgentes
    def test_ordena_por_prioridad(self):
        self.crear(prioridad='BAJA')
        self.crear(prioridad='URGENTE')
        self.crear(prioridad='MEDIA')

        response = self.client.get('/api/solicitudes/', {'ordering': '-prioridad'})
        prioridades = [s['prioridad'] for s in response.data['results']]
        self.assertEqual(prioridades, ['URGENTE', 'MEDIA', 'BAJA'])

        response = self.client.get('/api/solicitudes/', {'ordering': 'color'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#=========================================================================================
    # Permisos: sin token, Consulta no crea pero si consulta
    def test_permisos(self):
        self.client.force_authenticate(user=self.consulta)
        response = self.client.post('/api/solicitudes/', self.datos_validos())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get('/api/solicitudes/').status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=None)
        self.assertEqual(
            self.client.get('/api/solicitudes/').status_code,
            status.HTTP_401_UNAUTHORIZED)

    # Reporte: solicitudes por edificio y por estado
    def test_reporte_por_edificio(self):
        otro = Edificio.objects.create(nombre='Biblioteca', codigo='BI')
        sala = Espacio.objects.create(edificio=otro, nombre='Sala', tipo='AULA', piso=1)
        self.crear()
        self.crear(estado='CANCELADA')
        self.crear(espacio=sala)

        response = self.client.get('/api/reportes/solicitudes-por-edificio/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        datos = {e['edificio']: e for e in response.data}
        self.assertEqual(datos['Edificio A']['total'], 2)
        self.assertEqual(datos['Edificio A']['por_estado'], {'ABIERTA': 1, 'CANCELADA': 1})
        self.assertEqual(datos['Biblioteca']['total'], 1)

        self.client.force_authenticate(user=None)
        self.assertEqual(
            self.client.get('/api/reportes/solicitudes-por-edificio/').status_code,
            status.HTTP_401_UNAUTHORIZED)
