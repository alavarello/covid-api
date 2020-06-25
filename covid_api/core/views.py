from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Province
from .services import CovidService, DataFrameWrapper


class ProcessDataView(APIView):

    def process_data(self, request, data: DataFrameWrapper, **kwargs) -> DataFrameWrapper:
        return data

    def filter_data(self, request, data: DataFrameWrapper, **kwargs) -> DataFrameWrapper:
        icu = request.GET.get('icu', None)
        if icu is not None:
            value = 'SI' if icu.lower() == "true" else 'NO'
            data = data.filter('cuidado_intensivo', value)
        respirator = request.GET.get('respirator', None)
        if respirator is not None:
            value = 'SI' if respirator.lower() == "true" else 'NO'
            data = data.filter('asistencia_respiratoria_mecanica', value)
        dead = request.GET.get('dead', None)
        if dead is not None:
            value = 'SI' if dead.lower() == "true" else 'NO'
            data = data.filter('fallecido', value)
        return data

    def create_response(self, request, data: DataFrameWrapper, **kwargs) -> Response:
        return Response(data.to_json())

    def get(self, request, **kwargs):
        data = CovidService.get_data()
        data = self.filter_data(request, data, **kwargs)
        data = self.process_data(request, data, **kwargs)
        response = self.create_response(request, data, **kwargs)
        return response


class CountView(ProcessDataView):

    def create_response(self, request, data: DataFrameWrapper, **kwargs) -> Response:
        """
        Return a list of all users.
        """
        return Response({'count': data.count()})


class SummaryView(ProcessDataView):

    def create_response(self, request, data: DataFrameWrapper, **kwargs) -> Response:
        """
        Return a list of all users.
        """
        return Response(data.summary().to_json())


class ActiveCasesView(ProcessDataView):

    def process_data(self, request, data: DataFrameWrapper, **kwargs) -> DataFrameWrapper:
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

        return active_cases_per_day


class ProvinceListView(ProcessDataView):

    def process_data(self, request, data: DataFrameWrapper, province_slug=None, **kwargs) -> Response:
        """
        Return a list of all users.
        """
        province = Province.from_slug(province_slug)
        summary = data.filter(
            'carga_provincia_nombre',
            province
        )
        return summary


class ProvinceCountView(ProvinceListView, CountView):
    pass


class ProvinceSummaryView(ProvinceListView, SummaryView):
    pass
