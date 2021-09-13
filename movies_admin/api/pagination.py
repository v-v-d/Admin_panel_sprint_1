from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response


class PrimitivePagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('prev', self.page.previous_page_number() if self.page.has_previous() else 1),
            ('next', self.page.next_page_number()),
            ('results', data)
        ]))
