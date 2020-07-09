from datetime import datetime

from covid_api.core.services import CovidService


def update_data():
    print(f"Start updating file at: {datetime.now()}")
    CovidService.update_data()
    print(f"Finish updating file at: {datetime.now()}")
