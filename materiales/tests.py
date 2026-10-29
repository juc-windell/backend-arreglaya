from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Material

#=========================================================================================
class MaterialesAPITest(APITestCase):
    def setUp(self):
        Usuario = get_user_model()
        self.admin = Usuario.objects.create_user(
            username='admin_prueba', password='ClaveSegura123!')
        self.admin.groups.add(Group.objects.create(name='Administrador'))
        self.client.force_authenticate(user=self.admin)

    # Crear material: el codigo se guarda en mayusculas; codigo repetido da 400
    def test_crea_material_y_codigo_repetido(self):
        datos = {'codigo': 'cab01', 'nombre': 'Cable', 'stock_actual': 5}
        response = self.client.post('/api/materiales/', datos)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['codigo'], 'CAB01')

        response = self.client.post('/api/materiales/', datos)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Filtros ?activo= y ?search=; activo invalido da 400
    def test_filtros(self):
        Material.objects.create(codigo='CAB01', nombre='Cable', activo=True)
        Material.objects.create(codigo='LAM01', nombre='Lampara', activo=False)

        response = self.client.get('/api/materiales/', {'activo': 'false'})
        self.assertEqual(response.data['count'], 1)

        response = self.client.get('/api/materiales/', {'search': 'cab'})
        self.assertEqual(response.data['count'], 1)

        response = self.client.get('/api/materiales/', {'activo': 'talvez'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
