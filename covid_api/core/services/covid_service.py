import json
import os

import pandas as pd

from covid_api.settings import COVID_FILE_NAME


class DataFrameWrapper:
    data_frame = None

    def __init__(self, data_frame):
        self.data_frame = data_frame

    def count(self):
        # Count rows
        return len(self.data_frame.index)

    def copy(self):
        return DataFrameWrapper(self.data_frame.copy())

    def filter_eq(self, column, value):
        self.data_frame = self.data_frame.loc[self.data_frame[column] == value]
        return self

    def filter_ge(self, column, value):
        self.data_frame = self.data_frame.loc[self.data_frame[column] >= value]
        return self

    def filter_le(self, column, value):
        self.data_frame = self.data_frame.loc[self.data_frame[column] <= value]
        return self

    def group_by(self, columns):
        self.data_frame = self.data_frame.groupby(columns)
        return self

    def size(self):
        self.data_frame = self.data_frame.size()
        return self

    def summary(self):
        self.data_frame = self.data_frame.describe()
        return self

    def to_json(self, orient="table"):
        df = self.data_frame.reset_index(drop=True)
        json_string = df.to_json(orient=orient)
        return json.loads(json_string)['data']

    def __getitem__(self, column):
        return self.data_frame[column]


class CovidService:

    _raw_data = None

    data_url = 'https://sisa.msal.gov.ar/datos/descargas/covid-19/files/Covid19Casos.csv'

    @classmethod
    def get_data(cls) -> DataFrameWrapper:
        if cls._raw_data is None:
            # Try to get the data from a file first
            if os.path.isfile(COVID_FILE_NAME):
                cls._raw_data = pd.read_csv(
                    COVID_FILE_NAME,
                    encoding='utf-16'
                )
            else:
                # Update the data from the url and save the file
                cls.update_data()
        return DataFrameWrapper(cls._raw_data.copy(deep=True))

    @classmethod
    def update_data(cls):
        cls._raw_data = pd.read_csv(
            cls.data_url,
            encoding='utf-16'
        )
        cls._raw_data.to_csv(COVID_FILE_NAME, index=False, encoding='utf-16')
