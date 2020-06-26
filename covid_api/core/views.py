from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Province
from .services import CovidService, DataFrameWrapper

# ----- GENERIC VIEWS ----- #


class ProcessDataView(APIView):

    def process_data(self, request, data: DataFrameWrapper, **kwargs) -> DataFrameWrapper:
        return data

    def filter_data(self, request, data: DataFrameWrapper, **kwargs) -> DataFrameWrapper:
        data.filter_eq('clasificacion_resumen', 'Confirmado')
        icu = request.GET.get('icu', None)
        if icu is not None:
            value = 'SI' if icu.lower() == "true" else 'NO'
            data = data.filter_eq('cuidado_intensivo', value)
        respirator = request.GET.get('respirator', None)
        if respirator is not None:
            value = 'SI' if respirator.lower() == "true" else 'NO'
            data = data.filter_eq('asistencia_respiratoria_mecanica', value)
        dead = request.GET.get('dead', None)
        if dead is not None:
            value = 'SI' if dead.lower() == "true" else 'NO'
            data = data.filter_eq('fallecido', value)
        from_date = request.GET.get('from', None)
        if from_date is not None:
            data = data.filter_ge('fecha_diagnostico', from_date)
        to_date = request.GET.get('to', None)
        if to_date is not None:
            data = data.filter_le('fecha_diagnostico', to_date)

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
        last_update = data['ultima_actualizacion'].max()
        dead_data = data.copy()
        confirmed_data = data.copy()
        summary = {
            'total_fallecidos': dead_data.filter_eq('fallecido', 'SI').count(),
            'nuevos_fallecidos': dead_data.filter_eq('fecha_fallecimiento', last_update).count(),
            'total_confirmados': confirmed_data.count(),
            'nuevos_confirmados': confirmed_data.filter_eq('fecha_diagnostico', last_update).count(),
            'ultima_actualizacion': last_update
        }

        return Response(summary)


# --- ACTIVE CASE VIEWS --- #

class ActiveCasesView(ProcessDataView):

    def filter_data(self, request, data: DataFrameWrapper, **kwargs) -> DataFrameWrapper:
        data = super(ProcessDataView).filter_data(request, data, **kwargs)
        data = data.filter_eq(
            'clasificacion_resumen',
            'Confirmado'
        )
        return data

    def process_data(self, request, data: DataFrameWrapper, **kwargs) -> DataFrameWrapper:
        """
        Return a list of all users.
        """
        data = CovidService.get_data()
        active_cases_per_day = data.group_by(
            'fecha_diagnostico'
        ).size()

        return active_cases_per_day


# --- PROVINCE VIEWS --- #

class ProvinceListView(ProcessDataView):

    def process_data(self, request, data: DataFrameWrapper, province_slug=None, **kwargs) -> Response:
        """
        Return a list of all users.
        """
        province = Province.from_slug(province_slug)
        summary = data.filter_eq(
            'carga_provincia_nombre',
            province
        )
        return summary


class ProvinceCountView(ProvinceListView, CountView):
    pass


class ProvinceSummaryView(ProvinceListView, SummaryView):
    pass


# --- PROVINCES VIEWS --- #

class ProvincesListView(ProcessDataView):

    def create_response(self, request, data: DataFrameWrapper, **kwargs) -> Response:
        return Response(Province.PROVINCES)


class ProvincesProcessView(ProcessDataView):

    def process_data(self, request, data: DataFrameWrapper, **kwargs) -> DataFrameWrapper:
        """
        Return a list of all users.
        """
        data = CovidService.get_data()
        provinces = data.group_by(
            'carga_provincia_nombre',
        )

        return provinces
