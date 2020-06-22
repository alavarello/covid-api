# Argentine COVID-19 API

## Installation
```shell script
# Clone repo using ssh
git clone git@github.com:alavarello/covid-api.git
# Create a virtual environment
python3 -m venv env
# Activate
source env/bin/activate  # On Windows use `env\Scripts\activate`

# Install Django and Django REST framework into the virtual environment
pip install -r requirements.txt

# Run migrations
python manage.py migrate
```

## Run
Make sure the port 8000 is not being used
```shell script
python manage.py runserver
```

## Docs
```shell script
# Access swagger
http://localhost:8000/api/swagger/
# Access redoc
http://localhost:8000/api/redoc/
```