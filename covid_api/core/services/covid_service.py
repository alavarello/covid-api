import json

import pandas as pd


class CovidService:

    class DataFrameWrapper:
        data_frame = None

        def __init__(self, data_frame):
            self.data_frame = data_frame

        def count(self):
            # Count rows
            return len(self.data_frame.index)

        def filter(self, column, value):
            self.data_frame = self.data_frame.loc[self.data_frame[column] == value]
            return self

        def group_by(self, columns):
            self.data_frame = self.data_frame.groupby(columns)
            return self

        def size(self):
            self.data_frame = self.data_frame.size()
            return self

        def to_json(self, orient="table"):
            json_string = self.data_frame.to_json(orient=orient)
            return json.loads(json_string)['data']

    _raw_data = None

    _instance = None

    def __init__(self):
        dataframe = pd.read_csv(
            'https://sisa.msal.gov.ar/datos/descargas/covid-19/files/Covid19Casos.csv',
            encoding='utf-16'
        )
        self._raw_data = dataframe

    @classmethod
    def get_data(cls):
        if not cls._instance:
            cls._instance = CovidService()
        return cls.DataFrameWrapper(cls._instance._raw_data)
