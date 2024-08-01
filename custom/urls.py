from django.urls import path
import custom.views as custom

app_name = 'custom'

urlpatterns = [
    path('add_album_page/', custom.add_album_page, name='add_album_page'),
    path('add_album/', custom.add_album, name='add_album'),
    path('add_fileset_page/', custom.add_fileset_page, name='add_fileset_page'),
    path('add_fileset/', custom.add_fileset, name='add_fileset'),
    path('<str:url>/', custom.constructor, name='constructor'),
]