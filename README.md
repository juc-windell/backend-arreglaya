# ArreglaYa - API de mantenimiento del campus

API REST hecha con Django y Django REST Framework para ordenar el mantenimiento de una sede universitaria. Una falla se reporta, se asigna a un técnico, se atiende con una orden de trabajo y se cierra descontando los materiales usados del inventario.

Módulos: **Espacios**, **Técnicos**, **Solicitudes**, **Órdenes de trabajo** y **Materiales**. Además: usuarios, perfiles (grupos) y autenticación por token.
## Miembros del proyecto
- Windell Urróz Cortes
- Enzo Bejarano Mejías
- David Chang Castañeda

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

El detalle de cada endpoint (acceso, filtros y códigos de respuesta) está en [`docs/catalogo_endpoints.md`](docs/catalogo_endpoints.md).

| Método | Ruta | Descripción |
|---|---|---|
| POST | /api/token/ | Obtener token |
| GET | /api/perfil/ | Datos y grupos del usuario del token |
| GET, POST | /api/edificios/ | Listar / crear edificios |
| GET, PUT, PATCH, DELETE | /api/edificios/{id}/ | Ver / actualizar / eliminar edificio |
| GET, POST | /api/espacios/ | Listar / crear espacios |
| GET, PUT, PATCH, DELETE | /api/espacios/{id}/ | Ver / actualizar / eliminar espacio |
| GET, POST | /api/tecnicos/ | Listar (filtros `especialidad`, `activo`) / crear técnicos |
| GET, PUT, PATCH, DELETE | /api/tecnicos/{id}/ | Ver / actualizar / eliminar técnico |
| GET, POST | /api/solicitudes/ | Listar (filtros, orden y paginación) / crear solicitudes |
| GET, PUT, PATCH, DELETE | /api/solicitudes/{id}/ | Ver / actualizar / eliminar solicitud |
| GET, POST | /api/materiales/ | Listar (filtros y paginación) / crear materiales |
| GET, PUT, PATCH, DELETE | /api/materiales/{id}/ | Ver / actualizar / eliminar material |
| GET, POST | /api/ordenes/ | Listar (filtros y paginación) / crear órdenes de trabajo |
| GET, PUT, PATCH, DELETE | /api/ordenes/{id}/ | Ver / actualizar / eliminar orden (DELETE responde 409) |
| GET, POST | /api/ordenes/{id}/materiales/ | Ver / registrar materiales usados en una orden |
| GET | /api/ordenes/consultas/ | Consultas con agregación de órdenes y materiales |
| GET | /api/reportes/tiempo-por-tecnico/ | Días promedio de resolución por técnico |
| GET | /api/reportes/solicitudes-por-edificio/ | Solicitudes por edificio y por estado |

## Filtros, orden y paginación

- Los listados de solicitudes, órdenes y materiales están paginados: devuelven `count`, `next`, `previous` y `results`, con 5 registros por página, y se navegan con `?page=2`. Una página que no existe responde **404**.
- Solicitudes: `?estado=`, `?prioridad=`, `?categoria=`, `?espacio=` y `?ordering=fecha_reporte|-fecha_reporte|prioridad|-prioridad`.
- Órdenes: `?estado=` y `?tecnico=`. Materiales: `?activo=true|false` y `?search=`. Técnicos: `?especialidad=` y `?activo=`.
- Un valor inválido en `activo`, `espacio` u `ordering` responde **400**.
- El tamaño de página se cambia en `PAGE_SIZE` de `settings.py`.

## Reglas de las solicitudes

- Una solicitud nueva siempre inicia **ABIERTA** y `reportado_por` es el usuario del token.
- Estados: ABIERTA, ASIGNADA, EN_PROCESO, RESUELTA y CANCELADA. ASIGNADA y EN_PROCESO se asignan solos al crear y avanzar la orden de trabajo.
- Pasa a RESUELTA solo si su orden está FINALIZADA (**409** en otro caso). RESUELTA y CANCELADA no se modifican (**409**).
- Una solicitud con orden no se elimina (**409**) ni cambia de categoría.

## Matriz de permisos

| Recurso | Administrador | Operador | Consulta |
|---|---|---|---|
| Edificios, Espacios, Técnicos, Materiales | Todo | Solo GET | Solo GET |
| Solicitudes, Órdenes | Todo | GET, POST, PUT, PATCH | Solo GET |

Las órdenes de trabajo no se eliminan: `DELETE /api/ordenes/{id}/` responde **409** porque se conservan como historial.

Sin token: **401**. Con token pero sin permiso: **403**.

## Postman

Importar `postman/ArreglaYa.postman_collection.json`. En las variables de la colección, poner en `password_prueba` la misma clave de `PASSWORD_USUARIOS_PRUEBA`. Ejecutar primero la carpeta **1. Autenticacion** para guardar los tokens.