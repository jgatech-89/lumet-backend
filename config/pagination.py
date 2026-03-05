from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Paginación por página con tamaño configurable por query param."""

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_page_size(self, request):
        if self.page_size_query_param and request.query_params.get(self.page_size_query_param):
            try:
                size = int(request.query_params[self.page_size_query_param])
                return min(size, self.max_page_size)
            except (ValueError, TypeError):
                pass
        return self.page_size
