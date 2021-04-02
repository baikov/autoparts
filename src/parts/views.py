from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound, NotAcceptable
from parts.serializers import PartSerializer
from .models import Part


class SmallPagesPagination(PageNumberPagination):
    page_size = 40


class PartViewset(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PartSerializer
    pagination_class = SmallPagesPagination

    def get_queryset(self):
        vin = self.request.query_params.get('vin', None)
        if vin is not None:
            parts = Part.objects.filter(vin=vin)
            if parts:
                return parts
            else:
                raise NotFound()
        else:
            raise NotAcceptable()
        # return parts
