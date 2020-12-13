from django.db import models

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
