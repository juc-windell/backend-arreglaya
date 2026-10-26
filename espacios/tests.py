from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Edificio, Espacio

#==========================================================================================
class EspaciosAPITest(APITestCase):
    def setUp(self):
        Usuario = get_user_model()

        self.admin = Usuario.objects.create_user(
            username='admin_prueba', password='ClaveSegura123!')
        self.admin.groups.add(Group.objects.create(name='Administrador'))

        self.consulta = Usuario.objects.create_user(
            username='consulta_prueba', password='ClaveSegura123!')
        self.consulta.groups.add(Group.objects.create(name='Consulta'))

        self.edificio = Edificio.objects.create(nombre='Edificio A', codigo='EA')
        self.espacio = Espacio.objects.create(
            edificio=self.edificio, nombre='Aula 101', tipo='AULA', piso=1)
        
#========================================================================================
    # El administrador crea un edificio 
    def test_admin_crea_edificio(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(reverse('api_edificios'), {
            'nombre': 'Edificio C',
            'codigo': 'ec',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['codigo'], 'EC')

#=========================================================================================
    # El administrador actualiza un espacio con PATCH 
    def test_admin_actualiza_espacio(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('detalle_espacio', args=[self.espacio.id])
        response = self.client.patch(url, {'piso': 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['piso'], 3)

#==========================================================================================
    # El administrador elimina un espacio 
    def test_admin_elimina_espacio(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('detalle_espacio', args=[self.espacio.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

#==========================================================================================
    # No se repite el nombre de un edificio 
    def test_nombre_edificio_repetido(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(reverse('api_edificios'), {
            'nombre': 'Edificio A',
            'codigo': 'EA2',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nombre', response.data)

#=========================================================================================
    # No se repite un espacio en el mismo edificio
    def test_espacio_repetido_en_edificio(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(reverse('api_espacios'), {
            'edificio': self.edificio.id,
            'nombre': 'Aula 101',
            'tipo': 'AULA',
            'piso': 1,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#=======================================================================================
    # El piso no puede ser negativo
    def test_patch_piso_negativo(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('detalle_espacio', args=[self.espacio.id])
        response = self.client.patch(url, {'piso': -1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('piso', response.data)

#=======================================================================================
    # No se elimina un edificio con espacios 
    def test_no_elimina_edificio_con_espacios(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('detalle_edificio', args=[self.edificio.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Edificio.objects.filter(id=self.edificio.id).exists())

#======================================================================================
    # Sin token responde
    def test_sin_token(self):
        response = self.client.get(reverse('api_edificios'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#=========================================================================================
    # El perfil Consulta puede ver pero no crear 
    def test_consulta_no_puede_crear(self):
        self.client.force_authenticate(user=self.consulta)
        response = self.client.get(reverse('api_espacios'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse('api_espacios'), {
            'edificio': self.edificio.id,
            'nombre': 'Aula 102',
            'tipo': 'AULA',
            'piso': 1,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#==============================================================================================
    # El edificio no existe
    def test_edificio_no_existe(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('detalle_edificio', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)