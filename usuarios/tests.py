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
#=========================================================================================
# Proyecto 2: logout con revocacion del token
class LogoutAPITest(APITestCase):
    def setUp(self):
        Usuario = get_user_model()
        self.usuario = Usuario.objects.create_user(
            username='beto',
            password='ClaveSegura123!'
        )
        self.token = Token.objects.create(user=self.usuario)

    # El perfil informa si el usuario es superusuario
    def test_perfil_incluye_is_superuser(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(reverse('api_perfil'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_superuser'])

    # Logout borra el token y luego ese token responde 401
    def test_logout_revoca_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(reverse('api_logout'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())

        response = self.client.get(reverse('api_perfil'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Logout sin token responde 401
    def test_logout_sin_token(self):
        response = self.client.post(reverse('api_logout'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
