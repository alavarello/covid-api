from django.conf.urls import url
from django.urls import path

from covid_api.core import views

urlpatterns = [
    path('', views.ProcessDataView.as_view(), name='all'),
    path('count/', views.CountView.as_view(), name='all-count'),
    path('summary/', views.SummaryView.as_view(), name='all-summary'),
    path('last_update/', views.LastUpdateView.as_view(), name='last-update'),
    path('provinces/', views.ProvincesListView.as_view(), name='provinces-view'),
    path('province/<str:province_slug>/', views.ProvinceListView.as_view(), name='province-view'),
    path('province/<str:province_slug>/count/', views.ProvinceCountView.as_view(), name='province-count-view'),
    path('province/<str:province_slug>/summary/', views.ProvinceSummaryView.as_view(), name='province-summary-view'),
]
