from django.db import models

# Create your models here.
class Province:

    # Source: https://sitioanterior.indec.gob.ar/ftp/cuadros/menusuperior/clasificadores/anexo1_resol55_2019.pdf
    PROVINCES = {
        '02': 'CABA',
        '06': 'Buenos Aires',
        '10': 'Catamarca',
        '14': 'Córdoba',
        '18': 'Corrientes',
        '22': 'Chaco',
        '26': 'Chubut',
        '30': 'Entre Ríos',
        '34': 'Formosa',
        '38': 'Jujuy',
        '42': 'La Pampa',
        '46': 'La Rioja',
        '50': 'Mendoza',
        '54': 'Misiones',
        '58': 'Neuquén',
        '62': 'Río Negro',
        '66': 'Salta',
        '70': 'San Juan',
        '74': 'San Luis',
        '78': 'Santa Cruz',
        '82': 'Santa Fe',
        '86': 'Santiago del Estero',
        '90': 'Tucumán',
        '94': 'Tierra del Fuego',
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


