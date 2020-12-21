# Argentine COVID-19 API

This API uses the [Argentinian Ministry of Health (msal.gob.ar) dataset](http://datos.salud.gob.ar/dataset/covid-19-casos-registrados-en-la-republica-argentina)

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
python3 -m venv env
# Activate
source env/bin/activate  # On Windows use `env\Scripts\activate`

# Install Django and Django REST framework into the virtual environment
pip3 install -r requirements.txt

# Create .env file
cp docs/env.txt covid_api/.env  # In development
cp docs/env_production.txt covid_api/.env # In production

# Download csv
wget https://sisa.msal.gov.ar/datos/descargas/covid-19/files/Covid19Casos.csv -O /tmp/Covid19Casos.csv

# Run migrations
python3 manage.py migrate
```

**Important**: Once you copy the env file change the secret key for a random string 

## Update data

**Important**: Always make sure you have the `env` activated before running any command.

To add the cron that updates the data.
```shell script
python3 manage.py crontab add
```

To force the update
```shell script
python3 manage.py update_data
```

**Note**: This may take up to an hour to update.
 
## Run

**Important**: Always make sure you have the `env` activated before running any command.

### Development
Make sure the port 8000 is not being used.
```shell script
python3 manage.py runserver
```

### Production
Make sure the port 8000 is not being used.
```shell script
gunicorn covid_api.wsgi --workers 3 --timeout 600 --bind 0.0.0.0:8000 -D
```
#### EB deploy
```
eb init --region sa-east-1 -p python-3.6 covid_api_django
eb create django-env
eb deploy
```

## Docs
```shell script
# Access swagger
http://localhost:8000/api/v1/swagger/
```
