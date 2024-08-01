"""
URL configuration for MedProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.conf.urls.static import static
from MedProject import settings
import main.views as main
from django.views.i18n import JavaScriptCatalog
from main.decorators import check_recaptcha
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_tools/', include('admin_tools.urls')),

    path('', main.index, name='index'),
    path('reviews/', main.ReviewsList.as_view(), name='reviews'),
    path('reviews/<int:page>/', main.ReviewsList.as_view(), name='reviews_page'),
    path('create_review/', check_recaptcha(main.create_review), name='create_review'),
    path('faq/', main.FaqView.as_view(), name='faq'),
    path('faq/<int:page>/', main.FaqView.as_view(), name='faq_page'),
    path('create_question/', check_recaptcha(main.create_question), name='create_question'),
    path('consultation/', main.consultation, name='consultation'),
    path('create_application/', check_recaptcha(main.create_application), name='create_application'),
    path('geography/', main.geography, name='geography'),
    path('news/', main.NewsList.as_view(), name='news'),
    path('news/<int:page>/', main.NewsList.as_view(), name='news_page'),
    path('single_news/<int:pk>/', main.single_news, name='single_news'),

    path('custom/', include('custom.urls', namespace='custom')),
    path('authentication/', include('authentication.urls', namespace='authentication')),
    path('specialists/', include('specialists.urls', namespace='specialists')),

    path('editor/', include('django_summernote.urls')),
    path('jsi18n', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('password-reset/', PasswordResetView.as_view(template_name='authentication/password_reset.html'), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='authentication/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
