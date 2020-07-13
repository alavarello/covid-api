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

# Create .env file
cp docs/env.txt covid_api/.env  # In development
cp docs/env_production.txt covid_api/.env # In production
```

Once you copy the env file change the secrete key for a random string 

## Run

Make sure the port 8000 is not being used.
```shell script
gunicorn covid_api.wsgi --workers 3 --timeout 600 --bind 0.0.0.0:8000 -D
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
