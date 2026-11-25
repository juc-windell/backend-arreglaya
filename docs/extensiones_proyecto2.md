# Ampliaciones del backend para el Proyecto 2 (frontend React)

Responsable: Persona 1. Todas mantienen las reglas de negocio y los permisos del Proyecto 1. Pruebas: `python manage.py test` (53 pruebas, 5 nuevas).

| # | Cambio | Archivos | Motivo | Seguridad |
|---|---|---|---|---|
| 1 | CORS con `django-cors-headers` y `CORS_ALLOWED_ORIGINS` en `.env` | `settings.py`, `requirements.txt`, `.env.example` | El navegador bloquea las peticiones de `http://localhost:5173` a `http://127.0.0.1:8000` si Django no autoriza el origen | Solo se permiten los orígenes de la lista; no se usa `CORS_ALLOW_ALL_ORIGINS` |
| 2 | `POST /api/logout/` borra el token del usuario (204) | `usuarios/views.py`, `usuarios/urls.py` | El enunciado pide explicar si el token se revoca; ahora sí se revoca en el servidor | Requiere token válido (401 sin token). Luego del logout el token viejo responde 401 |
| 3 | `is_superuser` en `GET /api/perfil/` | `usuarios/views.py` | `es_administrador()` trata al superusuario como Administrador aunque no tenga grupo; el frontend necesita saberlo para mostrar sus acciones | Solo lectura del propio usuario |
| 4 | `edificio_nombre` (solo lectura) en espacios | `espacios/serializers.py` | Mostrar la relación Espacio → Edificio en el listado sin una consulta por fila | No se puede escribir; el POST/PUT sigue usando `edificio` (id) |
| 5 | Filtros `?edificio=<id>` y `?tipo=<TIPO>` combinables en `GET /api/espacios/` | `espacios/views.py` | Filtrar en el servidor (no localmente) y listar los espacios de un edificio en su detalle | Valores inválidos → 400 |

Pruebas nuevas: `LogoutAPITest` (3) en `usuarios/tests.py` y `EspaciosFiltrosAPITest` (2) en `espacios/tests.py`.
