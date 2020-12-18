import xlrd
import json
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_csv.renderers import CSVRenderer

from .models import Province, Classification
from .services import CovidService, QueryWrapper
from .parameters import DateParameter, ClassificationParameter


# -------- UTILS -------- #

def df_to_json_table(df):
    df = df.reset_index(drop=True)
    json_string = df.to_json(orient='table')
    return json.loads(json_string)['data']


# ----- GENERIC VIEWS ----- #

class ProcessDataView(APIView):

    renderer_classes = [JSONRenderer, CSVRenderer]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filters = None

    def process_data(self, request, query: QueryWrapper, **kwargs):
        return query.to_json()

    @staticmethod
    def filter_data(request, query: QueryWrapper, **kwargs):
        equal_filters = {}
        classification = request.GET.get('classification', None)
        if classification is not None:
            classification = Classification.translate(classification.lower())
            query.filter_eq('clasificacion_resumen', classification)
            equal_filters['clasificacion_resumen'] = classification
        icu = request.GET.get('icu', None)
        if icu is not None:
            value = 'SI' if icu.lower() == "true" else 'NO'
            query.filter_eq('cuidado_intensivo', value)
            equal_filters['cuidado_intensivo'] = value
        respirator = request.GET.get('respirator', None)
        if respirator is not None:
            value = 'SI' if respirator.lower() == "true" else 'NO'
            query.filter_eq('asistencia_respiratoria_mecanica', value)
            equal_filters['asistencia_respiratoria_mecanica'] = value
        dead = request.GET.get('dead', None)
        if dead is not None:
            value = 'SI' if dead.lower() == "true" else 'NO'
            query.filter_eq('fallecido', value)
            equal_filters['fallecido'] = value
        from_date = request.GET.get('from', None)
        if from_date is not None:
            if dead == 'true':
                query.filter_ge('fecha_fallecimiento', from_date)
            else:
                query.filter_ge('fecha_diagnostico', from_date)
        to_date = request.GET.get('to', None)
        if to_date is not None:
            if dead == 'true':
                query.filter_le('fecha_fallecimiento', to_date)
            else:
                query.filter_le('fecha_diagnostico', to_date)
        return equal_filters

    def create_response(self, request, json_obj, **kwargs) -> Response:
        return Response(json_obj)

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
        query = CovidService.get_query()
        self.filters = self.filter_data(request, query, **kwargs)
        json_obj = self.process_data(request, query, **kwargs)
        response = self.create_response(request, json_obj, **kwargs)
        self.filters = None
        return response


class CountView(ProcessDataView):
    """
    Returns the amount of cases after applying the filters
    """

    renderer_classes = [JSONRenderer, ]

    def process_data(self, request, query: QueryWrapper, **kwargs) -> int:
        return query.count()

    def create_response(self, request, count, **kwargs) -> Response:
        return Response({'count': count})


# --- PROVINCE VIEWS --- #

class ProvinceListView(ProcessDataView):
    """
    Returns the cases for the given province
    """

    def process_data(self, request, query: QueryWrapper, province_slug=None, **kwargs):
        province = Province.from_slug(province_slug)
        if province is None:
            return []
        return query.filter_eq(
            'carga_provincia_nombre',
            province['name']
        ).to_json()


class ProvinceCountView(ProvinceListView, CountView):
    """
    Returns the amount of cases after applying the filters for the given province
    """
    def process_data(self, request, query: QueryWrapper, province_slug=None, **kwargs):
        province = Province.from_slug(province_slug)
        if province is None:
            return []
        return query.filter_eq(
            'carga_provincia_nombre',
            province['name']
        ).count()


class ProvinceSummaryView(ProcessDataView):

    def process_data(self, request, query: QueryWrapper, province_slug=None, **kwargs):
        from_date = request.GET.get('from', None)
        to_date = request.GET.get('to', None)

        province = Province.from_slug(province_slug)
        if province is None:
            return []

        df = CovidService.summary(province['name'], from_date, to_date, self.filters)
        df = CovidService.population_summary_metrics(df, province_slug)
        return df_to_json_table(df)

# --- PROVINCES VIEWS --- #

class ProvincesListView(APIView):
    """
    Returns the provinces with their respective slug
    """

    def get(self, request) -> Response:
        province_array = [{'slug': slug, **province} for slug, province in Province.PROVINCES.items()]
        return Response(province_array)


# --- LAST UPDATE VIEW --- #

class LastUpdateView(APIView):
    """
    Returns the date that the file was last updated
    """

    def get(self, request, **kwargs):
        last_update = CovidService.get_query().get_last_update_date()
        return Response({'last_update': last_update})


# --- COUNTRY SUMMARY VIEW --- #

class CountrySummaryView(ProcessDataView):

    def process_data(self, request, data: QueryWrapper, **kwargs) -> QueryWrapper:
        from_date = request.GET.get('from', None)
        to_date = request.GET.get('to', None)

        df = CovidService.summary(None, from_date, to_date, self.filters)
        df = CovidService.population_summary_metrics(df, None)
        return df_to_json_table(df)


# --- METRICS VIEW --- #
class StatsView(APIView):
    """
    Returns the provinces and country stats.
    """

    @staticmethod
    def province_stats(province_name, query, population):
        # Get population from 2020
        cases_amount = query.count()
        cases_per_million = cases_amount * 1000000 / population
        cases_per_hundred_thousand = cases_amount * 100000 / population
        dead_amount = query.filter_eq('fallecido', 'SI').count()
        dead_per_million = dead_amount * 1000000 / population
        dead_per_hundred_thousand = dead_amount * 100000 / population
        stats = {
                'provincia': province_name,
                'población': int(population),
                'muertes_por_millón': round(dead_per_million, 5),
                'muertes_cada_cien_mil': round(dead_per_hundred_thousand, 5),
                'casos_por_millón': round(cases_per_million, 5),
                'casos_cada_cien_mil': round(cases_per_hundred_thousand, 5),
                'letalidad': cases_amount if cases_amount == 0 else round(dead_amount / cases_amount, 4),
            }
        return stats

    def get(self, requests):
        workbook = xlrd.open_workbook('poblacion.xls')
        response = []

        for worksheet in workbook.sheets():
            split_name = worksheet.name.split('-')
            if len(split_name) < 2:
                continue

            # Filter the query
            query = CovidService.get_query()
            query.filter_eq('clasificacion_resumen', 'Confirmado')
            province_slug = split_name[0]
            province = Province.from_slug(province_slug)
            if province:
                province_name = province['name']
                query.filter_eq(
                    'carga_provincia_nombre',
                    province_name
                )
                population = worksheet.cell(16, 1).value
            else:
                province_name = "Argentina"
                population = worksheet.cell(15, 1).value

            province_stats = self.province_stats(
                province_name,
                query,
                population
            )
            response.append(province_stats)

        return Response(response)


class ProvinceStatsView(StatsView):
    """
    Returns a province stats.
    """
    def get(self, requests, province_slug=None):
        workbook = xlrd.open_workbook('poblacion.xls')
        data = CovidService.get_query()
        # Filter the data
        data = data.filter_eq('clasificacion_resumen', 'Confirmado')
        province = Province.from_slug(province_slug)
        if province is None:
            return Response([])
        province_name = province['name']
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