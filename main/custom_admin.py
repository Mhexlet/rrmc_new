# myapp/custom_admin.py
from django.contrib import admin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path
from .models import News  # Импортируем нужные модели
from django.contrib.admin import AdminSite
from django.shortcuts import render



class EmptyAdminSite(AdminSite):
    site_header = ("Пустая админка")
    site_title = ("Пустая панель")
    index_title = ("Добро пожаловать в пустую админку")

    def get_app_list(self, request):
        """
        Переопределяем метод get_app_list, чтобы вернуть пустой список приложений.
        Это полностью уберет приложения из панели администрирования.
        """
        return []
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = self.index_title
        return render(request, 'admin/index.html', extra_context)


empty_admin_site = EmptyAdminSite(name='empty_admin')

# empty_admin_site.register(News, admin.ModelAdmin)
