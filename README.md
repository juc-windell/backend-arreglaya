# ArreglaYa - API de mantenimiento del campus

API REST hecha con Django y Django REST Framework para ordenar el mantenimiento de una sede universitaria. Una falla se reporta, se asigna a un técnico, se atiende con una orden de trabajo y se cierra descontando los materiales usados del inventario.

Módulos: **Espacios**, **Técnicos**, **Solicitudes**, **Órdenes de trabajo** y **Materiales**. Además: usuarios, perfiles (grupos) y autenticación por token.

## Requisitos

- Python 3.12 o superior
- MySQL 8
- Git

## Instalación

```bash
git clone https://github.com/USUARIO/backend-arreglaya.git
cd backend-arreglaya
python -m venv .venv
source .venv/Scripts/activate      # Git Bash en Windows
pip install -r requirements.txt
cp .env.example .env               # luego edite .env con sus datos
```

### Base de datos

En MySQL:

```sql
CREATE DATABASE arreglaya_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Migraciones, datos de prueba y superusuario

```bash
python manage.py migrate
python manage.py crear_datos_prueba
python manage.py createsuperuser
```

`crear_datos_prueba` crea los grupos **Administrador**, **Operador** y **Consulta**, los usuarios `admin1`, `operador1` y `consulta1` (con la clave `PASSWORD_USUARIOS_PRUEBA` del `.env`), sus tokens y datos ficticios.

### Ejecución

```bash
python manage.py runserver
```

### Pruebas automatizadas

```bash
python manage.py test
```

## Autenticación

`POST /api/token/` con `username` y `password` devuelve un token. En cada solicitud se envía el encabezado:

```
Authorization: Token <token>
```

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | /api/token/ | Obtener token |
| GET | /api/perfil/ | Datos y grupos del usuario del token |
| GET, POST | /api/edificios/ | Listar / crear edificios |
| GET, PUT, PATCH, DELETE | /api/edificios/{id}/ | Ver / actualizar / eliminar edificio |
| GET, POST | /api/espacios/ | Listar / crear espacios |
| GET, PUT, PATCH, DELETE | /api/espacios/{id}/ | Ver / actualizar / eliminar espacio |
| GET, POST | /api/tecnicos/ | Listar / crear técnicos |
| GET, PUT, PATCH, DELETE | /api/tecnicos/{id}/ | Ver / actualizar / eliminar técnico |

## Matriz de permisos

| Recurso | Administrador | Operador | Consulta |
|---|---|---|---|
| Edificios, Espacios, Técnicos, Materiales | Todo | Solo GET | Solo GET |
| Solicitudes, Órdenes | Todo | GET, POST, PUT, PATCH | Solo GET |

Sin token: **401**. Con token pero sin permiso: **403**.

## Postman

Importar `postman/ArreglaYa.postman_collection.json`. En las variables de la colección, poner en `password_prueba` la misma clave de `PASSWORD_USUARIOS_PRUEBA`. Ejecutar primero la carpeta **1. Autenticacion** para guardar los tokens.

## Limitaciones conocidas

- No tiene frontend; se prueba con Postman y con las pruebas automatizadas.