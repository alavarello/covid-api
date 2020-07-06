from drf_yasg import openapi
from drf_yasg.openapi import Parameter


class DateParameter(Parameter):

    def __init__(self, name):
        super().__init__(
            name,  openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
            pattern="\d{4}-\d{2}-\d{2}"
        )
