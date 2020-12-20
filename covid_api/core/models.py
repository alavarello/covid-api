from django.db import models
from sqlalchemy.ext.declarative import declarative_base
from dbview.models import DbView
from dbview.helpers import CreateView


Base = declarative_base()

# Create your models here.
class Province:

    # Source: https://sitioanterior.indec.gob.ar/ftp/cuadros/menusuperior/clasificadores/anexo1_resol55_2019.pdf
    PROVINCES = {
        '02': {'name': 'CABA',                'lat': '-34.601167', 'long': '-58.444362'},
        '06': {'name': 'Buenos Aires',        'lat': '-36.435607', 'long': '-60.236047'},
        '10': {'name': 'Catamarca',           'lat': '-26.994342', 'long': '-67.301823'},
        '14': {'name': 'Córdoba',             'lat': '-31.933031', 'long': '-63.907306'},
        '18': {'name': 'Corrientes',          'lat': '-28.794180', 'long': '-57.788470'},
        '22': {'name': 'Chaco',               'lat': '-26.374994', 'long': '-60.392845'},
        '26': {'name': 'Chubut',              'lat': '-43.951260', 'long': '-68.613087'},
        '30': {'name': 'Entre Ríos',          'lat': '-31.907715', 'long': '-59.153529'},
        '34': {'name': 'Formosa',             'lat': '-25.169933', 'long': '-59.487736'},
        '38': {'name': 'Jujuy',               'lat': '-23.662247', 'long': '-65.214883'},
        '42': {'name': 'La Pampa',            'lat': '-37.247714', 'long': '-65.698473'},
        '46': {'name': 'La Rioja',            'lat': '-29.571620', 'long': '-66.951880'},
        '50': {'name': 'Mendoza',             'lat': '-33.954473', 'long': '-68.517431'},
        '54': {'name': 'Misiones',            'lat': '-26.941464', 'long': '-54.572184'},
        '58': {'name': 'Neuquén',             'lat': '-38.627263', 'long': '-69.870836'},
        '62': {'name': 'Río Negro',           'lat': '-40.203546', 'long': '-66.762142'},
        '66': {'name': 'Salta',               'lat': '-25.013085', 'long': '-64.560534'},
        '70': {'name': 'San Juan',            'lat': '-30.799658', 'long': '-68.979531'},
        '74': {'name': 'San Luis',            'lat': '-33.933585', 'long': '-66.122008'},
        '78': {'name': 'Santa Cruz',          'lat': '-48.667105', 'long': '-70.006752'},
        '82': {'name': 'Santa Fe',            'lat': '-30.568459', 'long': '-60.942796'},
        '86': {'name': 'Santiago del Estero', 'lat': '-27.673470', 'long': '-63.263549'},
        '90': {'name': 'Tucumán',             'lat': '-26.966970', 'long': '-65.435826'},
        '94': {'name': 'Tierra del Fuego',    'lat': '-54.279017', 'long': '-67.646957'},
    }

    @classmethod
    def from_slug(cls, slug):
        return cls.PROVINCES.get(slug, None)


class Classification:

    classifications = {
        'confirmed': 'Confirmado',
        'rejected': 'Descartado',
        'suspect': 'Sospechoso'
    }

    @classmethod
    def translate(cls, classification):
        data_classification = cls.classifications.get(classification)
        return data_classification


class CovidCase(models.Model):
    # TODO: configurar los máximos de los campos a su valor ideal.
    class Meta:
        index_together = [['carga_provincia_nombre', 'clasificacion_resumen', 'fecha_diagnostico', 'fallecido', 'cuidado_intensivo', 'asistencia_respiratoria_mecanica']]

    id_evento_caso = models.IntegerField(default=0, primary_key=True)
    sexo = models.CharField(max_length=1, null=True)
    edad = models.IntegerField(default=0, null=True)
    edad_años_meses = models.CharField(max_length=5, null=True)
    residencia_pais_nombre = models.CharField(max_length=20, null=True)
    residencia_provincia_nombre = models.CharField(max_length=40, null=True)
    residencia_departamento_nombre = models.CharField(max_length=80, null=True)
    carga_provincia_nombre = models.CharField(max_length=20)
    fecha_inicio_sintomas = models.DateField(null=True)
    fecha_apertura = models.DateField(null=True)
    sepi_apertura = models.IntegerField(default=0, null=True)
    fecha_internacion = models.DateField(null=True)
    cuidado_intensivo = models.CharField(max_length=2, null=True)
    fecha_cui_intensivo = models.DateField(null=True)
    fallecido = models.CharField(max_length=2, null=True)
    fecha_fallecimiento = models.DateField(null=True)
    asistencia_respiratoria_mecanica = models.CharField(max_length=2, null=True)
    carga_provincia_id = models.IntegerField(default=0, null=True)
    origen_financiamiento = models.CharField(max_length=20, null=True)
    clasificacion = models.CharField(max_length=80, null=True)
    clasificacion_resumen = models.CharField(max_length=12, null=True)
    residencia_provincia_id = models.IntegerField(default=0, null=True)
    fecha_diagnostico = models.DateField(null=True)
    residencia_departamento_id = models.IntegerField(default=0, null=True)
    ultima_actualizacion = models.DateField()


class CasesSummaryView(DbView):
    fecha_diagnostico = models.DateField(null=True)
    carga_provincia_nombre = models.CharField(max_length=20)
    casos = models.IntegerField(default=0)
    muertes = models.IntegerField(default=0)

    @classmethod
    def get_view_str(cls):
        """
        This method returns the SQL string that creates the view
        """
        return '''
            CREATE VIEW core_casessummaryview AS 
                select fecha_diagnostico, carga_provincia_nombre, clasificacion_resumen, cuidado_intensivo, asistencia_respiratoria_mecanica, fallecido, count(*) casos, count(case when fallecido = 'SI' then 1 end) muertes
                from core_covidcase
                where fecha_diagnostico is not null
                group by fecha_diagnostico, carga_provincia_nombre, clasificacion_resumen, cuidado_intensivo, asistencia_respiratoria_mecanica, fallecido
                order by fecha_diagnostico, carga_provincia_nombre;
                '''


class MyCreateView(CreateView):

    def _drop_view(self, model, schema_editor):
        sql_template = 'DROP VIEW IF EXISTS %(table)s '
        args = {
            'table': schema_editor.quote_name(model._meta.db_table),
        }
        sql = sql_template % args
        schema_editor.execute(sql, None)
