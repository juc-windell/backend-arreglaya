from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

#=========================================================================================
class TokenYPerfilAPITest(APITestCase):
    def setUp(self):
        Usuario = get_user_model()
        self.usuario = Usuario.objects.create_user(
            username='ana',
            password='ClaveSegura123!'
        )
        grupo = Group.objects.create(name='Consulta')
        self.usuario.groups.add(grupo)

    # El endpoint /api/token/ devuelve un token con usuario y clave correctos
    def test_obtiene_token(self):
        response = self.client.post(reverse('api_token'), {
            'username': 'ana',
            'password': 'ClaveSegura123!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    # Con el token en el encabezado Authorization se accede al perfil
    def test_perfil_con_token(self):
        token = Token.objects.create(user=self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(reverse('api_perfil'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['grupos'], ['Consulta'])

    # Sin token responde 401
    def test_perfil_sin_token(self):
        response = self.client.get(reverse('api_perfil'))
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )