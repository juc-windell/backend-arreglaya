from rest_framework.pagination import PageNumberPagination

#==================================================================================
# Pagina un queryset en una vista hecha con @api_view.
# Usa el PAGE_SIZE de settings.py (5) y el parametro ?page=
# Si la pagina no existe responde 404
def paginar(request, queryset, serializer_class):
    paginador = PageNumberPagination()
    pagina = paginador.paginate_queryset(queryset, request)
    serializer = serializer_class(pagina, many=True)
    return paginador.get_paginated_response(serializer.data)
