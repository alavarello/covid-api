from django.conf.urls import url

from covid_api.core import views

urlpatterns = [
    url(r'^count/', views.DataView.as_view(), name='count'),
    url(r'^list/', views.CountView.as_view(), name='list'),
]
