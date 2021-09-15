from collections import OrderedDict

from django.core.paginator import EmptyPage
from rest_framework import pagination
from rest_framework.response import Response


class PrimitivePagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        try:
            next_page_number = self.page.next_page_number()
        except EmptyPage:
            next_page_number = None

        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('prev', self.page.previous_page_number() if self.page.has_previous() else None),
            ('next', next_page_number),
            ('results', data)
        ]))
