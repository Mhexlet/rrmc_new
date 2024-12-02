from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
# from .views import StatisticsView
from anketa.views import StatisticsByInstitutionView, StatisticsByCityView, StatisticsByRelationView, StatisticsByContactView, StatisticsByAgeView



# urlpatterns = [
#     path('statistics/', StatisticsView.as_view(), name='anketa_statistics'),
# ]
urlpatterns = [
    path('statistics/institutions/', StatisticsByInstitutionView.as_view(), name='statistics_by_institution'),
    path('statistics/cities/', StatisticsByCityView.as_view(), name='statistics_by_city'),
    path('statistics/relations/', StatisticsByRelationView.as_view(), name='statistics_by_relation'),
    path('statistics/contact/', StatisticsByContactView.as_view(), name='statistics_by_contact'),
    path('statistics/time/', StatisticsByContactView.as_view(), name='statistics_by_time'),
    path('statistics/reasons/', StatisticsByContactView.as_view(), name='statistics_by_reasons'),
    path('statistics/sources/', StatisticsByContactView.as_view(), name='statistics_by_sources'),
    path('statistics/age/', StatisticsByAgeView.as_view(), name='statistics_by_age'),


]
