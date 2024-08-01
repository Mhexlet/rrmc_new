from django.urls import path
import specialists.views as spec
from main.decorators import check_recaptcha
from .views import SpecialistListView, FieldOfActivityListView


app_name = 'specialists'

urlpatterns = [
    path('account/', spec.account, name='account'),
    path('create_article_page/', spec.create_article_page, name='create_article_page'),
    path('create_article/', check_recaptcha(spec.create_article), name='create_article'),
    path('edit_article_page/<int:pk>/', spec.edit_article_page, name='edit_article_page'),
    path('edit_article/', check_recaptcha(spec.edit_article), name='edit_article'),
    path('delete_article/', spec.delete_article, name='delete_article'),
    path('delete_application/', spec.delete_application, name='delete_application'),
    path('hide_article/', spec.hide_article, name='hide_article'),
    path('profile/<int:pk>/', spec.profile, name='profile'),
    path('article/<int:pk>/', spec.article, name='article'),
    path('specialists/', spec.SpecialistsList.as_view(), name='specialists'),
    path('specialists/<int:page>/', spec.SpecialistsList.as_view(), name='specialists_page'),
    path('api/specialists/', SpecialistListView.as_view(), name='specialist_list'),
    path('api/fields_of_activity/', FieldOfActivityListView.as_view(), name='field-of-activity-list'),

]