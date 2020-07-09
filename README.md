# Argentine COVID-19 API

## Installation

Clone the repository using ssh or http

```shell script
# Clone repo using ssh
git clone git@github.com:alavarello/covid-api.git
# Clone repo using http
git clone https://github.com/alavarello/covid-api.git
``` 

Create the virtual environment and install all the requirements.\
For more information about virtual environments click [here](https://docs.python.org/3/library/venv.html#module-venv) \
The global python version must be > 3.6

```shell script
# Create a virtual environment
python -m venv env
# Activate
source env/bin/activate  # On Windows use `env\Scripts\activate`

# Install Django and Django REST framework into the virtual environment
pip install -r requirements.txt

# Run migrations
python manage.py migrate
```

## Run

Make sure the port 8000 is not being used.
```shell script
python manage.py runserver
```

To add the cron that updates the data.
```shell script
python manage.py crontab add
```

## Docs
```shell script
# Access swagger
http://localhost:8000/api/v1/swagger/
# Access redoc
http://localhost:8000/api/v1/redoc/
```