from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_csv.renderers import CSVRenderer
import pandas as pd

from .models import Province, Classification
from .services import CovidService, DataFrameWrapper
from .parameters import DateParameter, ClassificationParameter


# ----- GENERIC VIEWS ----- #

class ProcessDataView(APIView):

    renderer_classes = [JSONRenderer, CSVRenderer]

    def process_data(self, request, data: DataFrameWrapper, **kwargs) -> DataFrameWrapper:
        return data

    def filter_data(self, request, data: DataFrameWrapper, **kwargs) -> DataFrameWrapper:
        classification = request.GET.get('classification', None)
        if classification is not None:
            classification = Classification.translate(classification.lower())
            data.filter_eq('clasificacion_resumen', classification)
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

    @swagger_auto_schema(
        manual_parameters=[
            Parameter("icu", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            Parameter("dead", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            Parameter("respirator", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            ClassificationParameter(),
            DateParameter("from"),
            DateParameter("to"),
        ],
    )
    def get(self, request, **kwargs):
        data = CovidService.get_data()
        data = self.filter_data(request, data, **kwargs)
        data = self.process_data(request, data, **kwargs)
        response = self.create_response(request, data, **kwargs)
        return response


class CountView(ProcessDataView):
    """
    Returns the amount of cases after applying the filters
    """

    renderer_classes = [JSONRenderer, ]

    def create_response(self, request, data: DataFrameWrapper, **kwargs) -> Response:
        return Response({'count': data.count()})


# --- PROVINCE VIEWS --- #

class ProvinceListView(ProcessDataView):
    """
    Returns the cases for the given province
    """

    def process_data(self, request, data: DataFrameWrapper, province_slug=None, **kwargs) -> Response:
        province = Province.from_slug(province_slug)
        summary = data.filter_eq(
            'carga_provincia_nombre',
            province
        )
        return summary


class ProvinceCountView(ProvinceListView, CountView):
    """
    Returns the amount of cases after applying the filters for the given province
    """
    pass


class ProvinceSummaryView(ProcessDataView):

    def process_data(self, request, data: DataFrameWrapper, province_slug=None, **kwargs) -> DataFrameWrapper:
        from_date = request.GET.get('from', None)
        to_date = request.GET.get('to', None)

        province = Province.from_slug(province_slug)
        summary = data.filter_eq(
            'carga_provincia_nombre',
            province
        )

        summary = CovidService.summary(['carga_provincia_nombre'], from_date, to_date, summary)

        return summary


# --- PROVINCES VIEWS --- #

class ProvincesListView(APIView):
    """
    Returns the provinces with their respective slug
    """

    def get(self, request) -> Response:
        province_array = [{'slug': slug, 'province': province} for slug, province in Province.PROVINCES.items()]
        return Response(province_array)


# --- LAST UPDATE VIEW --- #

class LastUpdateView(APIView):
    """
    Returns the date that the file was last updated
    """

    def get(self, request, **kwargs):
        data = CovidService.get_data()
        last_update = data['ultima_actualizacion'].max()
        return Response({'last_update': last_update})


# --- COUNTRY SUMMARY VIEW --- #

class CountrySummaryView(ProcessDataView):

    def process_data(self, request, data: DataFrameWrapper, **kwargs) -> DataFrameWrapper:
        from_date = request.GET.get('from', None)
        to_date = request.GET.get('to', None)

        summary = CovidService.summary([], from_date, to_date, data)

        return summary