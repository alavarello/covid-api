import json
import os
from datetime import datetime, timedelta

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

    # Refresh time in hours
    refresh_rate = 1

    last_refresh = None

    @classmethod
    def get_data(cls) -> DataFrameWrapper:
        is_time_to_refresh = True

        if cls.last_refresh:
            refresh_time = cls.last_refresh + timedelta(hours=cls.refresh_rate)
            is_time_to_refresh = refresh_time < datetime.now()

        if cls._raw_data is None or is_time_to_refresh:
            if not os.path.isfile(COVID_FILE_NAME):
                # Update the data from the url and save the file
                cls.update_data()

            cls._raw_data = pd.read_csv(
                COVID_FILE_NAME,
                encoding='utf-8'
            )
            # Get the base hour
            cls.last_refresh = datetime.now().replace(
                minute=0,
                second=0,
                microsecond=0
            )
        return DataFrameWrapper(cls._raw_data)

    @classmethod
    def update_data(cls):
        data_frame = pd.read_csv(
            cls.data_url,
            encoding='utf-16'
        )
        data_frame.to_csv(COVID_FILE_NAME, index=False)
        cls._raw_data = None

    @classmethod
    def summary(cls, group_by_vector, start_date, end_date, data):

        start_date = start_date if start_date else '2020-02-11'
        end_date = end_date if end_date else data['ultima_actualizacion'].max()

        summary = data.data_frame

        range = pd.date_range(start=start_date, end=end_date)
        range_strings = range.format(formatter=lambda x: x.strftime('%Y-%m-%d'))
        df = pd.DataFrame(range_strings, columns=['fecha_diagnostico'])

        cases_count = summary.groupby(
            [elem for elem in group_by_vector] + ['fecha_diagnostico'],
            as_index=False
        ).count()
        df2 = cases_count[['fecha_diagnostico']].copy()
        df2['casos'] = cases_count['id_evento_caso']

        summary = summary.loc[summary['fallecido'] == 'SI']
        deaths_count = summary.groupby(
            [elem for elem in group_by_vector] + ['fecha_fallecimiento'],
            as_index=False
        ).count()[['fecha_fallecimiento', 'id_evento_caso']]
        deaths_count = deaths_count.rename(
            columns={'id_evento_caso': "muertes", 'fecha_fallecimiento': "fecha_diagnostico"})

        df = df.merge(df2, on='fecha_diagnostico', how='left')
        df = df.merge(deaths_count, on='fecha_diagnostico', how='left')

        df = df.fillna(value=0)

        df['muertes_acum'] = df['muertes'].cumsum()
        df['casos_acum'] = df['casos'].cumsum()

        return DataFrameWrapper(df)
