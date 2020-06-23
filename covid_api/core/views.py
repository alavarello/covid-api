from rest_framework.response import Response
from rest_framework.views import APIView

from .services import CovidService


class DataView(APIView):

    def get(self, request):
        """
        Return a list of all users.
        """
        covid_service = CovidService.get_data()
        response = {'count': covid_service.count()}
        return Response(response)


class CountView(APIView):

    def get(self, request):
        """
        Return a list of all users.
        """
        data = CovidService.get_data()
        active_cases_per_day = data.filter(
            'clasificacion_resumen',
            'Confirmado'
        ).group_by(
            'fecha_diagnostico'
        ).size()

        return Response(active_cases_per_day.to_json())
