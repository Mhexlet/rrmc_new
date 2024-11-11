from django import forms
from .models import Anketa
from django.utils import timezone





class StatisticsForm(forms.Form):
    start_date = forms.DateField(
        label="Дата начала",
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date() - timezone.timedelta(days=7)
    )
    end_date = forms.DateField(
        label="Дата окончания",
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()
    )
    show_top_10 = forms.BooleanField(
        label="Показать только топ-10 учреждений",
        required=False,
        initial=True
    )

















class AnketaForm(forms.ModelForm):
    class Meta:
        model = Anketa
        fields = [
            'last_name', 'first_name', 'middle_name',
            'relation', 'relation_other',
            'main_phone', 'additional_phone',
            'main_email', 'additional_email',
            'preferred_contact', 'preferred_time',
            'child_last_name', 'child_first_name', 'child_middle_name',
            'child_birth_date', 'city', 'street', 'house', 'apartment',
            'reasons', 'reason_other', 'referral_document',
            'sources', 'source_other', 'consent'
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={
                'class': 'med-input consultation-last-name',
                'placeholder': 'Фамилия'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'med-input consultation-first-name',
                'placeholder': 'Имя'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'med-input consultation-middle-name',
                'placeholder': 'Отчество'
            }),
            'relation': forms.RadioSelect(attrs={'class': 'med-input consultation-relation'}),
            'relation_other': forms.TextInput(attrs={
                'class': 'med-input consultation-relation-other',
                'placeholder': 'Иное (уточните)'
            }),
            'main_phone': forms.TextInput(attrs={
                'class': 'med-input consultation-phone',
                'placeholder': 'Основной номер телефона'
            }),
            'additional_phone': forms.TextInput(attrs={
                'class': 'med-input consultation-phone-additional',
                'placeholder': 'Дополнительный номер телефона'
            }),
            'main_email': forms.EmailInput(attrs={
                'class': 'med-input consultation-email',
                'placeholder': 'Основной электронный адрес'
            }),
            'additional_email': forms.EmailInput(attrs={
                'class': 'med-input consultation-email-additional',
                'placeholder': 'Дополнительный электронный адрес'
            }),
            'preferred_contact': forms.CheckboxSelectMultiple(attrs={'class': 'consultation-contact'}),
            'preferred_time': forms.RadioSelect(attrs={'class': 'consultation-time'}),
            'child_last_name': forms.TextInput(attrs={
                'class': 'med-input consultation-child-last-name',
                'placeholder': 'Фамилия ребенка'
            }),
            'child_first_name': forms.TextInput(attrs={
                'class': 'med-input consultation-child-first-name',
                'placeholder': 'Имя ребенка'
            }),
            'child_middle_name': forms.TextInput(attrs={
                'class': 'med-input consultation-child-middle-name',
                'placeholder': 'Отчество ребенка'
            }),
            'child_birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'med-input consultation-birth-date'
            }),
            'city': forms.TextInput(attrs={
                'class': 'med-input consultation-city',
                'placeholder': 'Город'
            }),
            'street': forms.TextInput(attrs={
                'class': 'med-input consultation-street',
                'placeholder': 'Улица/микрорайон'
            }),
            'house': forms.TextInput(attrs={
                'class': 'med-input consultation-house',
                'placeholder': 'Дом'
            }),
            'apartment': forms.TextInput(attrs={
                'class': 'med-input consultation-apartment',
                'placeholder': 'Квартира'
            }),
            'reason_other': forms.TextInput(attrs={
                'class': 'med-input consultation-reason-other',
                'placeholder': 'Иное (уточните)'
            }),
            'referral_document': forms.FileInput(attrs={'class': 'med-input consultation-document'}),
            'source_other': forms.TextInput(attrs={
                'class': 'med-input consultation-source-other',
                'placeholder': 'Иное (уточните)'
            }),
            'consent': forms.CheckboxInput(attrs={'class': 'consultation-consent'}),
        }

# anketa/forms.py
