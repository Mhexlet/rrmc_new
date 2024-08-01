from django.urls import path
import authentication.views as auth
from main.decorators import check_recaptcha

app_name = 'authentication'

urlpatterns = [
    path('login/', auth.login, name='login'),
    path('logout/', auth.logout, name='logout'),
    path('register/', auth.register, name='register'),
    path('edit_profile_page/', auth.edit_profile_page, name='edit_profile_page'),
    path('edit_profile/', check_recaptcha(auth.edit_profile), name='edit_profile'),
    path('edit_foas/', check_recaptcha(auth.edit_foas), name='edit_foas'),
    path('delete_application/', auth.delete_application, name='delete_application'),
    path('change_password/', auth.change_password, name='change_password'),
    path('verify/<str:email>/<str:key>/', auth.verify, name='verify'),
    path('send_verify_email_page/', auth.send_verify_email_page, name='send_verify_email_page'),
    path('renew_verification_key/', auth.renew_verification_key, name='renew_verification_key'),
    path('send_application/', auth.send_application, name='send_application'),
    path('rules/', auth.rules, name='rules'),
]
