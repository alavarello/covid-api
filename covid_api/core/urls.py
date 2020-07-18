from django.urls import path

from covid_api.core import views

urlpatterns = [
    path('count/', views.CountView.as_view(), name='all-count'),
    path('stats/', views.StatsView.as_view(), name='all-count'),
    path('summary/', views.CountrySummaryView.as_view(), name='country-summary-view'),
    path('last_update/', views.LastUpdateView.as_view(), name='last-update'),
    path('provinces/', views.ProvincesListView.as_view(), name='provinces-view'),
    path('province/<str:province_slug>/', views.ProvinceListView.as_view(), name='province-view'),
    path('province/<str:province_slug>/stats/', views.ProvinceStatsView.as_view(), name='province-stats-view'),
    path('province/<str:province_slug>/count/', views.ProvinceCountView.as_view(), name='province-count-view'),
    path('province/<str:province_slug>/summary/', views.ProvinceSummaryView.as_view(), name='province-summary-view'),
]
