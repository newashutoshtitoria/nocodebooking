from rest_framework.pagination import PageNumberPagination

class NumberUserPagination(PageNumberPagination):
    page_size = 10