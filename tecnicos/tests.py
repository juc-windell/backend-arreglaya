from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Tecnico

#===================================================================================
class TecnicosAPITest(APITestCase):
    def setUp(self):
        Usuario = get_user_model()

        self.admin = Usuario.objects.create_user(
            username='admin_prueba', password='ClaveSegura123!')
        self.admin.groups.add(Group.objects.create(name='Administrador'))

        self.operador = Usuario.objects.create_user(
            username='operador_prueba', password='ClaveSegura123!')
        self.operador.groups.add(Group.objects.create(name='Operador'))

        self.tecnico = Tecnico.objects.create(
            nombre='Carlos Mora',
            identificacion='101110111',
            especialidad='ELECTRICIDAD',
            telefono='88881111',
            max_ordenes_abiertas=3,
        )

#=====================================================================================
    # El administrador crea un tecnico
    def test_admin_crea_tecnico(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(reverse('api_tecnicos'), {
            'nombre': 'Luis Rojas',
            'identificacion': '202220222',
            'especialidad': 'PLOMERIA',
            'telefono': '88882222',
            'max_ordenes_abiertas': 2,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#======================================================================================
    # El operador puede listar los tecnicos
    def test_operador_lista_tecnicos(self):
        self.client.force_authenticate(user=self.operador)
        response = self.client.get(reverse('api_tecnicos'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

#========================================================================================
    # La identificacion no se repite
    def test_identificacion_repetida(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(reverse('api_tecnicos'), {
            'nombre': 'Otro Tecnico',
            'identificacion': '101110111',
            'especialidad': 'GENERAL',
            'telefono': '88885555',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('identificacion', response.data)

#========================================================================================
    # max_ordenes_abiertas debe ser al menos 1
    def test_patch_max_ordenes_cero(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('detalle_tecnico', args=[self.tecnico.id])
        response = self.client.patch(url, {'max_ordenes_abiertas': 0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#========================================================================================
    # Especialidad fuera de la lista (400)
    def test_especialidad_invalida(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('detalle_tecnico', args=[self.tecnico.id])
        response = self.client.patch(url, {'especialidad': 'PINTURA'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#=======================================================================================
    # El operador no puede eliminar tecnicos
    def test_operador_no_puede_eliminar(self):
        self.client.force_authenticate(user=self.operador)
        url = reverse('detalle_tecnico', args=[self.tecnico.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#====================================================================================
    # El administrador elimina un tecnico sin ordenes
    def test_admin_elimina_tecnico(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('detalle_tecnico', args=[self.tecnico.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#====================================================================================
    # Filtro por especialidad (no distingue mayusculas)
    def test_filtro_por_especialidad(self):
        Tecnico.objects.create(
            nombre='Luis Rojas', identificacion='202220222',
            especialidad='PLOMERIA', telefono='88882222')
        self.client.force_authenticate(user=self.operador)
        response = self.client.get(reverse('api_tecnicos'), {'especialidad': 'plomeria'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['especialidad'], 'PLOMERIA')

#====================================================================================
    # Filtro por activo, y 400 si el valor no es true o false
    def test_filtro_por_activo(self):
        Tecnico.objects.create(
            nombre='Pedro Solano', identificacion='404440444',
            especialidad='GENERAL', telefono='88884444', activo=False)
        self.client.force_authenticate(user=self.operador)

        response = self.client.get(reverse('api_tecnicos'), {'activo': 'false'})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], 'Pedro Solano')

        response = self.client.get(reverse('api_tecnicos'), {'activo': 'talvez'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#====================================================================================
    # Regla 1: el tecnico debe estar activo y tener la especialidad (o ser GENERAL)
    def test_puede_atender(self):
        self.assertTrue(self.tecnico.puede_atender('ELECTRICIDAD'))
        self.assertFalse(self.tecnico.puede_atender('PLOMERIA'))

        general = Tecnico.objects.create(
            nombre='Pedro Solano', identificacion='404440444',
            especialidad='GENERAL', telefono='88884444')
        self.assertTrue(general.puede_atender('AIRES'))

        general.activo = False
        self.assertFalse(general.puede_atender('AIRES'))
