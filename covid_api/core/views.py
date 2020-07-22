from datetime import datetime
from itertools import islice

import xlrd
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_csv.renderers import CSVRenderer

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
            if dead == 'true':
                data = data.filter_ge('fecha_fallecimiento', from_date)
            else:
                data = data.filter_ge('fecha_diagnostico', from_date)
        to_date = request.GET.get('to', None)
        if to_date is not None:
            if dead == 'true':
                data = data.filter_le('fecha_fallecimiento', to_date)
            else:
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

        if province:
            summary = CovidService.summary(['carga_provincia_nombre'], from_date, to_date, summary)
            summary = CovidService.population_summary_metrics(summary,province_slug)

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

        summary = CovidService.population_summary_metrics(summary, None)

        return summary


# --- METRICS VIEW --- #
class StatsView(APIView):
    """
    Returns the provinces and country stats.
    """

    def province_stats(self, province_name, province_data, population):
        # Get population from 2020
        cases_amount = province_data.count()
        cases_per_million = cases_amount * 1000000 / population
        cases_per_hundred_thousand = cases_amount * 100000 / population
        dead_amount = province_data.filter_eq('fallecido', 'SI').count()
        dead_per_million = dead_amount * 1000000 / population
        dead_per_hundred_thousand = dead_amount * 100000 / population
        stats = {
            province_name: {
                'población': int(population),
                'muertes_por_millón': round(dead_per_million),
                'muertes_cada_cien_mil': round(dead_per_hundred_thousand),
                'casos_por_millón': round(cases_per_million),
                'casos_cada_cien_mil': round(cases_per_hundred_thousand),
                'letalidad': round(dead_amount / cases_amount, 4),

            }}
        return stats

    def get(self, requests):
        workbook = xlrd.open_workbook('poblacion.xls')
        response = {}
        data = CovidService.get_data()
        # Filter the data
        data = data.filter_eq('clasificacion_resumen', 'Confirmado')
        for worksheet in workbook.sheets():
            split_name = worksheet.name.split('-')
            if len(split_name) < 2:
                continue

            province_slug = split_name[0]
            province_name = Province.from_slug(province_slug)
            if province_name:
                province_data = data.copy().filter_eq(
                    'carga_provincia_nombre',
                    province_name
                )
                population = worksheet.cell(16, 1).value
            else:
                province_data = data.copy()
                province_name = "Argentina"
                population = worksheet.cell(15, 1).value

            province_stats = self.province_stats(
                province_name,
                province_data,
                population
            )
            response.update(province_stats)

        return Response(response)


class ProvinceStatsView(StatsView):
    """
    Returns a province stats.
    """
    def get(self, requests, province_slug=None):
        workbook = xlrd.open_workbook('poblacion.xls')
        data = CovidService.get_data()
        # Filter the data
        data = data.filter_eq('clasificacion_resumen', 'Confirmado')
        province_name = Province.from_slug(province_slug)
        province_data = data.filter_eq(
            'carga_provincia_nombre',
            province_name
        )
        sheet_name = f'{province_slug}-{province_name.upper()}'
        population = workbook.sheet_by_name(sheet_name).cell(16, 1).value

        province_stats = self.province_stats(
            province_name,
            province_data,
            population
        )

        return Response(province_stats)