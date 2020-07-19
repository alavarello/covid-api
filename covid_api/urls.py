from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from covid_api.settings import SWAGGER_URL

repository = "https://github.com/alavarello/covid-api"
description = f"This API uses the [Argentinian Ministry of Health (msal.gob.ar) dataset](" \
              f"http://datos.salud.gob.ar/dataset/covid-19-casos-registrados-en-la-republica" \
              f"-argentina)\n Repository: {repository} "
schema_view = get_schema_view(
   openapi.Info(
      title="Argentine Covid-19 API",
      default_version='v1',
      description=description,
      license=openapi.License(name="Creative Commons License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   url=SWAGGER_URL
)


api_version = 'api/v1'

urlpatterns = [
    re_path(f'^{api_version}/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(f'^{api_version}/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(f'^{api_version}/', include('covid_api.core.urls')),
    path('admin/', admin.site.urls),
    re_path('^', RedirectView.as_view(pattern_name='schema-swagger-ui', permanent=False)),
]

