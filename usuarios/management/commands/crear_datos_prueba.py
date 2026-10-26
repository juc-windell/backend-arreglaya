import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from espacios.models import Edificio, Espacio
from tecnicos.models import Tecnico

#===========================================================================================
class Command(BaseCommand):
    help = 'Crea los grupos, los usuarios de prueba y datos ficticios'

    def handle(self, *args, **options):
        clave = os.getenv('PASSWORD_USUARIOS_PRUEBA')
        if not clave:
            self.stdout.write('Falta PASSWORD_USUARIOS_PRUEBA en el archivo .env')
            return

#========================================================================================
        # Grupos y usuarios de prueba con su token
        Usuario = get_user_model()
        usuarios = [
            ('admin1', 'Administrador'),
            ('operador1', 'Operador'),
            ('consulta1', 'Consulta'),
        ]

        for username, nombre_grupo in usuarios:
            grupo, creado = Group.objects.get_or_create(name=nombre_grupo)

            usuario, creado = Usuario.objects.get_or_create(username=username)
            usuario.set_password(clave)
            usuario.save()
            usuario.groups.add(grupo)

            token, creado = Token.objects.get_or_create(user=usuario)
            self.stdout.write(
                username + ' (' + nombre_grupo + ') token: ' + token.key
            )

#===========================================================================================
        # Datos inventados de edificios y espacios
        edificio_a, creado = Edificio.objects.get_or_create(
            nombre='Edificio A', defaults={'codigo': 'EA'})
        edificio_b, creado = Edificio.objects.get_or_create(
            nombre='Edificio B', defaults={'codigo': 'EB'})
        biblioteca, creado = Edificio.objects.get_or_create(
            nombre='Biblioteca', defaults={'codigo': 'BI'})

        espacios = [
            (edificio_a, 'Aula 101', 'AULA', 1),
            (edificio_a, 'Laboratorio de Computo 1', 'LABORATORIO', 2),
            (edificio_b, 'Oficina de Docentes', 'OFICINA', 1),
            (edificio_b, 'Baño Planta Baja', 'BAÑO', 0),
            (biblioteca, 'Zona Verde', 'EXTERIOR', 0),
        ]
        for edificio, nombre, tipo, piso in espacios:
            Espacio.objects.get_or_create(
                edificio=edificio,
                nombre=nombre,
                defaults={'tipo': tipo, 'piso': piso}
            )
#=================================================================================================
        # Datos inventados de tecnicos
        tecnicos = [
            ('Carlos Mora', '101110111', 'ELECTRICIDAD', '88881111', True, 3),
            ('Luis Rojas', '202220222', 'PLOMERIA', '88882222', True, 2),
            ('Ana Vargas', '303330333', 'AIRES', '88883333', True, 3),
            ('Pedro Solano', '404440444', 'GENERAL', '88884444', False, 1),
        ]
        for nombre, identificacion, especialidad, telefono, activo, maximo in tecnicos:
            Tecnico.objects.get_or_create(
                identificacion=identificacion,
                defaults={
                    'nombre': nombre,
                    'especialidad': especialidad,
                    'telefono': telefono,
                    'activo': activo,
                    'max_ordenes_abiertas': maximo,
                }
            )

        self.stdout.write('Datos de prueba creados correctamente')