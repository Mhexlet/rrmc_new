from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
import django.forms as forms
from datetime import datetime
import pytz
from django.conf import settings
import hashlib
from authentication.models import User, FieldOfActivity
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox


class UserLoginForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'med-input'
            field.help_text = ''
        self.fields['username'].widget.attrs['placeholder'] = 'Email'
        self.fields['password'].widget.attrs['placeholder'] = 'Пароль'


class UserRegisterForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
    birthdate = forms.DateField(input_formats=['%Y-%m-%d'], label='Дата рождения')
    field_of_activity = forms.MultipleChoiceField(choices=tuple(
        [(f.pk, f.name) for f in FieldOfActivity.objects.all()]), label='Сферы деятельности в ранней помощи')

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'last_name', 'first_name', 'patronymic', 'birthdate',
                  'field_of_activity', 'profession', 'city', 'workplace_address', 'workplace_name',
                  'phone_number', 'photo', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'med-input'
            field.widget.attrs['placeholder'] = field.label
            field.help_text = ''
        self.fields['photo'].widget.attrs['style'] = 'display: none;'
        self.fields['field_of_activity'].widget.attrs['class'] = 'register-field-of-activity'
        # self.fields['birthdate'].widget.attrs['class'] = 'med-input datepicker'

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        user.email_verified = False
        user.verification_key = hashlib.sha1(user.email.encode('utf8')).hexdigest()
        user.verification_key_expires = datetime.now(pytz.timezone(settings.TIME_ZONE))
        user.save()

        return user


class UserPasswordChangeForm(PasswordChangeForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2', 'captcha']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'med-input'
            field.help_text = ''
        self.fields['old_password'].widget.attrs['placeholder'] = 'Старый пароль'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Новый пароль'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Подтвердите пароль'