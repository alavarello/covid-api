import json
from datetime import datetime
import xlrd
import pandas as pd
from django.core.serializers.json import Serializer
from django.db.models import QuerySet, Max, Sum
from covid_api.core.models import Province, CovidCase
from django.conf import settings
from sqlalchemy import create_engine
import re


class QueryWrapper:
    query: QuerySet = None

    def __init__(self, filtered: QuerySet = None):
        if filtered is None:
            self.query = CovidCase.objects.filter()
        else:
            self.query = filtered

    def count(self) -> int:
        # Count rows
        return self.query.count()

    def copy(self):
        return QueryWrapper(self.query.all())

    def filter_eq(self, column, value):
        self.query = self.query.filter(**{column: value})
        return self

    def filter_ge(self, column, value):
        self.query = self.query.filter(**{column + '__gte': value})
        return self

    def filter_le(self, column, value):
        self.query = self.query.filter(**{column + '__lte': value})
        return self

    def to_json(self):
        json_string = JSONSerializer().serialize(self.query)
        return json.loads(json_string)

    def get_last_update_date(self):
        return self.query.aggregate(Max('ultima_actualizacion'))["ultima_actualizacion__max"]


class JSONSerializer(Serializer):
    def get_dump_object(self, obj):
        self._current[obj._meta.pk.name] = obj._get_pk_val()
        return self._current


class CovidService:

    TABLE_NAME = settings.DATABASES['default']['TABLE_NAME']
    data_url = 'https://sisa.msal.gov.ar/datos/descargas/covid-19/files/Covid19Casos.csv'

    # Refresh time in hours
    refresh_rate = 1

    last_refresh = None

    engine = create_engine('sqlite:////{}'.format(settings.DATABASES['default']['NAME']), echo=True)

    @classmethod
    def get_query(cls) -> QueryWrapper:
        return QueryWrapper()

    @classmethod
    def update_data(cls):
        # We read the entire CSV
        print("Downloading csv to data frame...", end=" ")
        data_frame = pd.read_csv(
            cls.data_url,
            encoding='utf-8'
        )
        print("Done")

        def clean_date_field(date: str):
            # date in the CSV is in the form m/d/yy or broken as null
            # and django needs it in dd-mm-yyyy
            if date is None or type(date) == float:
                return None
            # if format is correct, continue
            pattern = re.compile("^([0-9]{4}-[0-9]{2}-[0-9]{2})$")
            if bool(pattern.match(date)):
                return datetime.strptime(date, "%Y-%m-%d").date()
            # else
            return datetime.strptime(date, "%m/%d/%y").date()

        # We clean the date values
        # TODO encontrar otra forma de limpiar esto más eficientemente
        print("Cleaning Date fields...", end=" ")
        date_fields = ['fecha_inicio_sintomas', 'fecha_apertura', 'fecha_internacion', 'fecha_cui_intensivo', 'fecha_fallecimiento', 'fecha_diagnostico', 'ultima_actualizacion']
        for df in date_fields:
            data_frame[df] = data_frame[df].apply(clean_date_field)
        print("Done")
        # We remove all values from the table BUT WE DO NOT DROP IT
        # TODO En vez de vaciar la tabla, insertar los valores que hayan sido acutalizados
        print("Deleting prev table...", end=" ")
        CovidCase.objects.all().delete()
        print("Done")

        # We insert the new values
        # TODO encontrar el valor óptimo de chunksize
        data_frame.to_sql(cls.TABLE_NAME, con=cls.engine, if_exists='append', index=False, chunksize=50000)
        # Get the base hour
        cls.last_refresh = datetime.now().replace(
            minute=0,
            second=0,
            microsecond=0
        )

    @classmethod
    def population_per_province(cls):
        provinces_population = {}
        workbook = xlrd.open_workbook('poblacion.xls')

        for worksheet in workbook.sheets():
            split_name = worksheet.name.split('-')
            if len(split_name) < 2:
                continue
            province_slug = split_name[0]
            province_name = Province.from_slug(province_slug)
            if province_name:
                provinces_population[province_slug] = worksheet.cell(16, 1).value
                continue
            else:
                country_population = worksheet.cell(15, 1).value

        provinces_population['ARG'] = country_population

        return provinces_population

    @classmethod
    def population_summary_metrics(cls, df, slug):

        if slug:
            population = cls.population_per_province()[slug]
        else:
            population = cls.population_per_province()['ARG']

        HUNDRED_THOUSAND = 100000
        MILLION = 1000000

        # per hundred thousand
        df['casos_cada_cien_mil'] = round(df['casos'] * HUNDRED_THOUSAND / population, 5)
        df['muertes_cada_cien_mil'] = round(df['muertes'] * HUNDRED_THOUSAND / population, 5)
        df['casos_acum_cada_cien_mil'] = round(df['casos_acum'] * HUNDRED_THOUSAND / population, 5)
        df['muertes_acum_cada_cien_mil'] = round(df['muertes_acum'] * HUNDRED_THOUSAND / population, 5)

        # per million
        df['casos_por_millón'] = round(df['casos'] * MILLION / population, 5)
        df['muertes_por_millón'] = round(df['muertes'] * MILLION / population, 5)
        df['casos_acum_por_millón'] = round(df['casos_acum'] * MILLION / population, 5)
        df['muertes_acum_por_millón'] = round(df['muertes_acum'] * MILLION / population, 5)

        return df

    @classmethod
    def summary(cls, province_name, from_date, to_date, filters):
        from_date = from_date if from_date else '2020-02-11'
        if not to_date:
            to_date = CovidService.get_query().get_last_update_date()

        # todo cambiar format por algo sin sql injection
        province_name = province_name if province_name else ''

        filters_clause = ''
        if province_name and province_name != '':
            filters_clause = "and carga_provincia_nombre = '{prov}'".format(prov=province_name)

        for f, v in filters.items():
            filters_clause = "{c} and {f} = '{v}'".format(c=filters_clause, f=f, v=v)

        sql_query = '''
                
                select *,
                       sum(casos) over (order by fecha_diagnostico) as casos_acum,
                       sum(muertes) over (order by fecha_diagnostico) as muertes_acum
                from (
                         select fecha_diagnostico, sum(casos) casos, sum(muertes) muertes
                         from core_casessummaryview
                         where fecha_diagnostico <= '{to_date}' and fecha_diagnostico >= '{from_date}' {filters_clause}
                         group by fecha_diagnostico
                     )
                group by fecha_diagnostico
        '''.format(prov=province_name, to_date=to_date, from_date=from_date, filters_clause=filters_clause)

        accum_df = pd.read_sql_query(sql_query, cls.engine)

        # we clean the table
        accum_df = accum_df.rename(columns={'fecha_diagnostico': 'fecha'})
        return accum_df
