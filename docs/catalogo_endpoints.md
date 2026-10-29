# Catálogo de endpoints - ArreglaYa

Todas las rutas terminan en `/`. Todas, menos `/api/token/`, requieren el header `Authorization: Token <token>`.

## Perfiles y códigos

| Perfil | Qué puede hacer |
|---|---|
| Administrador | Todo, incluida la eliminación. |
| Operador | GET en todo. POST, PUT y PATCH en solicitudes, órdenes y consumo de materiales. |
| Consulta | Solo GET. |

- **200** consulta o actualización correcta, **201** creado, **204** eliminado.
- **400** datos inválidos (JSON con el detalle por campo).
- **401** falta el token o es inválido. **403** token válido sin permiso para esa operación.
- **404** el recurso o la página no existe.
- **409** conflicto con el estado actual (regla de negocio, estado final, cupo, stock) o recurso con registros asociados (`PROTECT`).

## Autenticación y usuarios

| Método | Ruta | Descripción | Acceso | Códigos |
|---|---|---|---|---|
| POST | /api/token/ | Obtener token con `username` y `password` | Público | 200 / 400 |
| GET | /api/perfil/ | Usuario del token y sus grupos | Autenticado | 200 / 401 |

## Edificios y espacios

| Método | Ruta | Descripción | Acceso | Códigos |
|---|---|---|---|---|
| GET | /api/edificios/ | Lista | Autenticado | 200 / 401 |
| POST | /api/edificios/ | Crear | Administrador | 201 / 400 / 401 / 403 |
| GET | /api/edificios/{id}/ | Detalle | Autenticado | 200 / 401 / 404 |
| PUT, PATCH | /api/edificios/{id}/ | Actualizar | Administrador | 200 / 400 / 401 / 403 / 404 |
| DELETE | /api/edificios/{id}/ | Eliminar (409 si tiene espacios) | Administrador | 204 / 401 / 403 / 404 / 409 |
| GET | /api/espacios/ | Lista | Autenticado | 200 / 401 |
| POST | /api/espacios/ | Crear | Administrador | 201 / 400 / 401 / 403 |
| GET | /api/espacios/{id}/ | Detalle | Autenticado | 200 / 401 / 404 |
| PUT, PATCH | /api/espacios/{id}/ | Actualizar | Administrador | 200 / 400 / 401 / 403 / 404 |
| DELETE | /api/espacios/{id}/ | Eliminar (409 si tiene solicitudes) | Administrador | 204 / 401 / 403 / 404 / 409 |

## Técnicos

| Método | Ruta | Descripción | Acceso | Códigos |
|---|---|---|---|---|
| GET | /api/tecnicos/ | Lista. Filtros: `?especialidad=`, `?activo=true\|false` | Autenticado | 200 / 400 / 401 |
| POST | /api/tecnicos/ | Crear | Administrador | 201 / 400 / 401 / 403 |
| GET | /api/tecnicos/{id}/ | Detalle | Autenticado | 200 / 401 / 404 |
| PUT, PATCH | /api/tecnicos/{id}/ | Actualizar | Administrador | 200 / 400 / 401 / 403 / 404 |
| DELETE | /api/tecnicos/{id}/ | Eliminar (409 si tiene órdenes) | Administrador | 204 / 401 / 403 / 404 / 409 |

## Solicitudes

Listado paginado de 5 en 5 con `?page=`.

| Método | Ruta | Descripción | Acceso | Códigos |
|---|---|---|---|---|
| GET | /api/solicitudes/ | Lista. Filtros: `?estado=`, `?prioridad=`, `?categoria=`, `?espacio=`. Orden: `?ordering=fecha_reporte\|-fecha_reporte\|prioridad\|-prioridad` (por defecto, las más recientes primero) | Autenticado | 200 / 400 / 401 / 404 |
| POST | /api/solicitudes/ | Crear. Inicia ABIERTA y `reportado_por` sale del token | Administrador, Operador | 201 / 400 / 401 / 403 |
| GET | /api/solicitudes/{id}/ | Detalle | Autenticado | 200 / 401 / 404 |
| PUT, PATCH | /api/solicitudes/{id}/ | Actualizar (ver reglas de estado) | Administrador, Operador | 200 / 400 / 401 / 403 / 404 / 409 |
| DELETE | /api/solicitudes/{id}/ | Eliminar (409 si tiene orden) | Administrador | 204 / 401 / 403 / 404 / 409 |
| GET | /api/reportes/solicitudes-por-edificio/ | Total de solicitudes por edificio y por estado | Autenticado | 200 / 401 |

Estados y transiciones: `ABIERTA` a `ASIGNADA` o `CANCELADA`; `ASIGNADA` a `EN_PROCESO` o `CANCELADA`; `EN_PROCESO` a `RESUELTA` o `CANCELADA`. `RESUELTA` y `CANCELADA` son finales y no se modifican.

## Órdenes de trabajo

Listado paginado de 5 en 5 con `?page=`.

| Método | Ruta | Descripción | Acceso | Códigos |
|---|---|---|---|---|
| GET | /api/ordenes/ | Lista. Filtros: `?estado=`, `?tecnico=` | Autenticado | 200 / 401 / 404 |
| POST | /api/ordenes/ | Crear. La solicitud pasa a ASIGNADA | Administrador, Operador | 201 / 400 / 401 / 403 / 409 |
| GET | /api/ordenes/{id}/ | Detalle | Autenticado | 200 / 401 / 404 |
| PUT, PATCH | /api/ordenes/{id}/ | Actualizar o cambiar de estado | Administrador, Operador | 200 / 400 / 401 / 403 / 404 / 409 |
| DELETE | /api/ordenes/{id}/ | No permitido: las órdenes se conservan como historial | Administrador | 401 / 403 / 409 |
| GET | /api/ordenes/{id}/materiales/ | Materiales usados en la orden | Autenticado | 200 / 401 / 404 |
| POST | /api/ordenes/{id}/materiales/ | Registrar material usado (descuenta stock) | Administrador, Operador | 201 / 400 / 401 / 403 / 404 / 409 |
| GET | /api/ordenes/consultas/ | Carga por técnico, consumo por material, órdenes por estado y materiales bajo el stock mínimo | Autenticado | 200 / 401 |
| GET | /api/reportes/tiempo-por-tecnico/ | Días promedio de resolución por técnico | Autenticado | 200 / 401 |

## Materiales

Listado paginado de 5 en 5 con `?page=`.

| Método | Ruta | Descripción | Acceso | Códigos |
|---|---|---|---|---|
| GET | /api/materiales/ | Lista. Filtros: `?activo=true\|false`, `?search=` (nombre o código) | Autenticado | 200 / 400 / 401 / 404 |
| POST | /api/materiales/ | Crear | Administrador | 201 / 400 / 401 / 403 |
| GET | /api/materiales/{id}/ | Detalle | Autenticado | 200 / 401 / 404 |
| PUT, PATCH | /api/materiales/{id}/ | Actualizar | Administrador | 200 / 400 / 401 / 403 / 404 |
| DELETE | /api/materiales/{id}/ | Eliminar (409 si fue usado en una orden) | Administrador | 204 / 401 / 403 / 404 / 409 |

## Reglas de negocio de solicitudes y órdenes

1. Una orden exige un técnico activo cuya especialidad coincida con la categoría de la solicitud (o sea GENERAL). Si no, 409.
2. Un técnico no supera su `max_ordenes_abiertas`. Si no, 409.
3. Solo una solicitud ABIERTA recibe una orden. Si no, 409.
4. `fecha_cierre` no puede ser anterior a `fecha_asignacion` y solo existe en una orden FINALIZADA.
5. Usar un material descuenta el stock y este no queda negativo. Si no, 409.
6. No se usan materiales inactivos. Si no, 409.
7. Una orden FINALIZADA no se edita ni admite materiales, tampoco con PATCH. Si no, 409.
8. Una solicitud pasa a RESUELTA solo cuando su orden está FINALIZADA. Si no, 409.
9. Un recurso con registros asociados no se elimina (`PROTECT`). Si no, 409.
10. Una solicitud con orden no cambia de categoría. Si no, 409.
