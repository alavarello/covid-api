import pandas as pd


class CovidService:

    _data = None

    _instance = None

    def __init__(self):
        self._data = pd.read_csv(
            'https://sisa.msal.gov.ar/datos/descargas/covid-19/files/Covid19Casos.csv',
            encoding='utf-16'
        )

    @classmethod
    def get_solo(cls):
        if not cls._instance:
            cls._instance = CovidService()
        return cls._instance

    def count(self):
        # Count rows
        return len(self._data.index)
