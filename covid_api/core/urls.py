from django.conf.urls import url
from django.urls import path

from covid_api.core import views

urlpatterns = [
    path('', views.ProcessDataView.as_view(), name='all'),
    path('count/', views.CountView.as_view(), name='all-count'),
    path('provinces/', views.ProvinceListView.as_view(), name='province-view'),
    path('province/<str:province_slug>/', views.ProvinceListView.as_view(), name='province-view'),
    path('province/<str:province_slug>/count/', views.ProvinceCountView.as_view(), name='province-count-view'),
    path('province/<str:province_slug>/summary/', views.ProvinceSummaryView.as_view(), name='province-summary-view'),
]
