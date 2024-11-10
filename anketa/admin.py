from django.contrib import admin
from .models import Anketa
from django.utils.html import format_html
from django.utils import timezone
from .models import CustomCRMUser
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomCRMUser
        fields = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_anketa_manager', 'is_news_manager')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomCRMUser
        fields = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_anketa_manager', 'is_news_manager')


@admin.register(CustomCRMUser)
class CustomCRMUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomCRMUser

    list_display = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_anketa_manager', 'is_news_manager']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    list_filter = ['is_staff', 'is_anketa_manager', 'is_news_manager']

    # Поля при создании нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_staff', 'is_anketa_manager', 'is_news_manager'),
        }),
    )

    # Поля при редактировании существующего пользователя
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        # ('Права доступа', {'fields': ('is_staff', 'is_superuser', 'is_anketa_manager', 'is_news_manager')}),
        ('Права доступа', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

  

    

@admin.register(Anketa)
class AnketaAdmin(admin.ModelAdmin):
    list_display = [
        'created_at', 'date_taken_in_work', 'last_name', 'first_name', 'relation_display', 'status_display', 'get_age_display', 'rating_display', 'is_hidden', 'responsible_user_display'
    ]
    readonly_fields = [
        'status',
        'child_age_in_months', 'date_taken_in_work', 'date_processed',
        'date_feedback_received', 'created_at',
        'preferred_contact_display', 'reasons_display', 'sources_display', 'get_age_display', 'referral_document_link', 'responsible_user'
    ]
    fieldsets = (
        ("Информация о заявителе", {
            'fields': ('last_name', 'first_name', 'middle_name', 'relation', 'relation_other')
        }),
        ("Контактные данные", {
            'fields': ('main_phone', 'additional_phone', 'main_email', 'additional_email', 'preferred_contact_display', 'preferred_time')
        }),
        # ("Информация о ребенке", {
        #     'fields': ('child_last_name', 'child_first_name', 'child_middle_name', 'child_birth_date', 'child_age_in_months')
        # }),
        ("Информация о ребенке", {
            'fields': ('child_last_name', 'child_first_name', 'child_middle_name', 'child_birth_date', 'get_age_display')
        }),
        ("Адрес проживания", {
            'fields': ('city', 'street', 'house', 'apartment')
        }),
        ("Причины обращения", {
            'fields': ('reasons_display', 'reason_other')
        }),
        # ("Документ и согласие", {
        #     'fields': ('referral_document', )
        # }),
        ("Документ и согласие", {
            'fields': ('referral_document_link',)
        }),

        ("Выберете учреждение для направления", {
            'fields': ('institution',)
        }),
        
        ("Источник информации", {
            'fields': ('sources_display', 'source_other')
        }),
        ("Комментарий администратора", {
            'fields': ('admin_comment',)
        }),

        ("Статус и оценка", {
            'fields': ('status', 'rating', 'date_taken_in_work', 'date_processed', 'date_feedback_received', 'created_at')
        }),
    )
    list_filter = ['status', 'rating', 'created_at', 'is_hidden', 'relation']
    search_fields = ['last_name', 'first_name', 'child_last_name', 'main_phone']
    # Добавляем возможность сортировки
    ordering = ['-created_at', '-date_taken_in_work', '-date_processed', '-rating']

    def responsible_user_display(self, obj):
            if obj.responsible_user:
                return f"{obj.responsible_user.first_name} {obj.responsible_user.last_name}"
            return "Не назначен"

    responsible_user_display.short_description = "Ответственный пользователь"

    # Метод для отображения ссылки на документ
    def referral_document_link(self, obj):
        if obj.referral_document:
            return format_html(
                '<a href="{}" target="_blank">Открыть документ</a>',
                obj.referral_document.url
            )
        return "Документ не загружен"
    referral_document_link.short_description = "Наличие документа"

    def get_age_display(self, obj):
        return obj.get_age_display()
    get_age_display.short_description = "Возраст ребенка (годы, месяцы)"

    def relation_display(self, obj):
        return obj.get_relation_display()
    relation_display.short_description = "Степень родства"

    def status_display(self, obj):
        status_colors = {
            'new': '#FFA500',
            'in_progress': 'lightyellow',
            'processed': 'lightgreen',
            'feedback_received': '#87CEFA',  # Sky Blue (ещё один голубой оттенок)
        }
        color = status_colors.get(obj.status, 'white')
        return format_html(
            '<span style="background-color: {}; padding: 5px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = "Статус заявки"

    def rating_display(self, obj):
        return obj.get_rating_display() if obj.rating else "Не оценено"
    rating_display.short_description = "Оценка"

    # Отображение предпочтительного способа связи
    def preferred_contact_display(self, obj):
        choices = dict(Anketa.CONTACT_CHOICES)
        contacts = obj.preferred_contact
        if isinstance(contacts, list):
            contact_labels = [choices.get(contact, contact) for contact in contacts]
            return ', '.join(contact_labels)
        return contacts
    preferred_contact_display.short_description = "Предпочтительный способ связи"

    # Отображение причин обращения
    def reasons_display(self, obj):
        choices = dict(Anketa.REASON_CHOICES)
        reasons = obj.reasons
        if isinstance(reasons, list):
            reason_labels = [choices.get(reason, reason) for reason in reasons]
            return ', '.join(reason_labels)
        return reasons
    reasons_display.short_description = "Причины обращения"

    # Отображение источников информации
    def sources_display(self, obj):
        choices = dict(Anketa.SOURCE_CHOICES)
        sources = obj.sources
        if isinstance(sources, list):
            source_labels = [choices.get(source, source) for source in sources]
            return ', '.join(source_labels)
        return sources
    sources_display.short_description = "Источник информации"

    # Метод, вызываемый при открытии заявки в админке
    def change_view(self, request, object_id, form_url='', extra_context=None):
        anketa = self.get_object(request, object_id)

        if anketa and anketa.status == 'new':
            # Изменяем статус на "В работе" и устанавливаем текущую дату
            anketa.status = 'in_progress'
            anketa.date_taken_in_work = timezone.now().date()
            anketa.responsible_user = request.user
            anketa.save()

        return super().change_view(request, object_id, form_url, extra_context)

    # Переопределение метода save_model для автоматического обновления статуса и дат
    def save_model(self, request, obj, form, change):
        if change:
            original = Anketa.objects.get(pk=obj.pk)
            
            if original.status == 'new' and obj.status == 'new':
                obj.status = 'in_progress'
                obj.date_taken_in_work = timezone.now().date()

            if (not original.institution and obj.institution) or (original.institution != obj.institution):
                obj.status = 'processed'
                obj.date_processed = timezone.now().date()

            if (original.rating != obj.rating) and obj.rating is not None:
                obj.status = 'feedback_received'
                obj.date_feedback_received = timezone.now().date()
        else:
            obj.status = 'new'

        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }