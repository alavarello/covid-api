from django.db import models

# Create your models here.
class Province:

    PROVINCES = {
        'BA': 'Buenos Aires',
        'CT': 'Catamarca',
        'CABA': 'CABA',
        'CC': 'Chaco',
        'CH': 'Chubut',
        'CBA': 'Córdoba',
        'CR': 'Corrientes',
        'ER': 'Entre Ríos',
        'FO': 'Formosa',
        'JY': 'Jujuy',
        'LP': 'La Pampa',
        'LR': 'La Rioja',
        'MZ': 'Mendoza',
        'MS': 'Misiones',
        'NQ': 'Neuquén',
        'RN': 'Río Negro',
        'SA': 'Salta',
        'SJ': 'San Juan',
        'SL': 'San Luis',
        'SC': 'Santa Cruz',
        'SF': 'Santa Fe',
        'SE': 'Santiago del Estero',
        'TF': 'Tierra del Fuego',
        'TM': 'Tucumán',
    }

    @classmethod
    def from_slug(cls, slug):
        return cls.PROVINCES.get(slug, None)
