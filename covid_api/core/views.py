from rest_framework.response import Response
from rest_framework.views import APIView

from .services import CovidService


class DataView(APIView):

    def get(self, request):
        """
        Return a list of all users.
        """
        covid_service = CovidService.get_solo()
        response = {'count': covid_service.count()}
        return Response(response)
