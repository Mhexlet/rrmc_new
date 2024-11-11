from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
# from .views import StatisticsView
from anketa.views import StatisticsByInstitutionView, StatisticsByCityView, StatisticsByRelationView



# urlpatterns = [
#     path('statistics/', StatisticsView.as_view(), name='anketa_statistics'),
# ]
urlpatterns = [
    path('statistics/institutions/', StatisticsByInstitutionView.as_view(), name='statistics_by_institution'),
    path('statistics/cities/', StatisticsByCityView.as_view(), name='statistics_by_city'),
    path('statistics/relations/', StatisticsByRelationView.as_view(), name='statistics_by_relation'),

]
