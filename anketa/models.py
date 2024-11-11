from django.db import models
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from main.models import Place, Institution
from authentication.models import User
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver



class CustomCRMUser(User):
    is_anketa_manager = models.BooleanField(default=False, verbose_name="Может работать с анкетами")
    is_news_manager = models.BooleanField(default=False, verbose_name="Может работать с новостями")

    class Meta:
        verbose_name = "Пользователь CRM"
        verbose_name_plural = "Пользователи CRM"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    


# Модель для анкеты
class Anketa(models.Model):
    # ФИО заявителя
    last_name = models.CharField(max_length=100, verbose_name="Фамилия заявителя")
    first_name = models.CharField(max_length=100, verbose_name="Имя заявителя")
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество заявителя")

    # Степень родства
    RELATION_CHOICES = [
        ('parent', 'Родитель'),
        ('representative', 'Законный представитель'),
        ('other', 'Иное'),
    ]
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES, verbose_name="Степень родства")
    relation_other = models.CharField(max_length=200, blank=True, null=True, verbose_name="Иное (уточнить)")

    # Телефоны
    main_phone = models.CharField(max_length=20, verbose_name="Основной номер телефона")
    additional_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Дополнительный номер телефона")

    # Электронные адреса
    main_email = models.EmailField(verbose_name="Основной электронный адрес")
    additional_email = models.EmailField(blank=True, null=True, verbose_name="Дополнительный электронный адрес")

    # Предпочтительный способ связи
    CONTACT_CHOICES = [
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
        ('call', 'Звонок'),
    ]
    preferred_contact = models.JSONField(verbose_name="Предпочтительный способ связи")

    # Удобное время для связи
    TIME_CHOICES = [
        ('morning', 'с 10:00 до 13:00'),
        ('afternoon', 'с 14:00 до 17:00'),
    ]
    preferred_time = models.CharField(max_length=20, choices=TIME_CHOICES, verbose_name="Удобное время для связи")

    # ФИО ребенка
    child_last_name = models.CharField(max_length=100, verbose_name="Фамилия ребенка")
    child_first_name = models.CharField(max_length=100, verbose_name="Имя ребенка")
    child_middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество ребенка")

    # Дата рождения ребенка
    child_birth_date = models.DateField(verbose_name="Дата рождения ребенка")
    
    # Возраст ребенка в месяцах (будет рассчитан автоматически)
    child_age_in_months = models.PositiveIntegerField(editable=False, verbose_name="Возраст ребенка в месяцах")

    # Адрес проживания ребенка
    # city = models.CharField(max_length=100, verbose_name="Город")
    city = models.ForeignKey(
        'main.Place',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Город",
        related_name='anketas'
    )

    institution = models.ForeignKey(
        'main.Institution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Учреждение',
        related_name='anketas'
    )
    street = models.CharField(max_length=200, verbose_name="Улица/микрорайон")
    house = models.CharField(max_length=20, verbose_name="Дом")
    apartment = models.CharField(max_length=20, blank=True, null=True, verbose_name="Квартира")

    # Причины обращения
    REASON_CHOICES = [
        ('disability', 'Ребенок-инвалид'),
        ('health_group', 'IV или V группа здоровья'),
        ('developmental_issues', 'Особенности физического/психического развития'),
        ('parent_concern', 'Обеспокоенность родителей'),
        ('other', 'Иное'),
    ]
    reasons = models.JSONField(verbose_name="Причины обращения")
    reason_other = models.CharField(max_length=200, blank=True, null=True, verbose_name="Иное (уточнить)")

    # Документ направления
    referral_document = models.FileField(upload_to='referrals/', blank=True, null=True, verbose_name="Документ направления")

    # Источник информации о службе
    SOURCE_CHOICES = [
        ('healthcare', 'От специалиста учреждения здравоохранения'),
        ('education', 'От специалиста учреждения образования'),
        ('social_protection', 'От специалиста учреждения социальной защиты'),
        ('media', 'Из СМИ'),
        ('other', 'Иное'),
    ]
    sources = models.JSONField(verbose_name="Источник информации")
    source_other = models.CharField(max_length=200, blank=True, null=True, verbose_name="Иное (уточнить)")

    # Согласие на обработку данных
    consent = models.BooleanField(default=False, verbose_name="Согласие на обработку персональных данных")

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    # Статус заявки
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('processed', 'Обработана'),
        ('feedback_received', 'Получена обратная связь'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус заявки")

    # Оценка по 5-балльной шкале (выпадающий список)
    RATING_CHOICES = [
        (1, '1 - Очень плохо'),
        (2, '2 - Плохо'),
        (3, '3 - Удовлетворительно'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        blank=True,
        null=True,
        verbose_name="Оценка"
    )

    # Комментарий (только для админки)
    admin_comment = models.TextField(blank=True, null=True, verbose_name="Комментарий администратора")

    # Даты этапов обработки
    date_taken_in_work = models.DateField(blank=True, null=True, verbose_name="Дата взятия в работу")
    date_processed = models.DateField(blank=True, null=True, verbose_name="Дата обработки")
    date_feedback_received = models.DateField(blank=True, null=True, verbose_name="Дата получения обратной связи")

    # Чекбокс для скрытия заявки
    is_hidden = models.BooleanField(default=False, verbose_name="Скрыта")

    # Добавляем поле для ответственного пользователя
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Ответственный пользователь"
    )

    # Переопределение метода save для автоматического расчёта возраста в месяцах
    def save(self, *args, **kwargs):
        if self.child_birth_date:
            # Если дата рождения представлена в виде строки, преобразуем её в объект `date`
            if isinstance(self.child_birth_date, str):
                try:
                    self.child_birth_date = datetime.strptime(self.child_birth_date, '%Y-%m-%d').date()
                except ValueError:
                    self.child_birth_date = None

            # Проверяем, что дата рождения корректна и вычисляем возраст
            if isinstance(self.child_birth_date, date):
                age_delta = relativedelta(date.today(), self.child_birth_date)
                self.child_age_in_months = age_delta.years * 12 + age_delta.months
            else:
                self.child_age_in_months = 0

        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "Анкета (заявка на раннюю помощь)"
        verbose_name_plural = "Анкеты (заявки на раннюю помощь)"

    def __str__(self):
        # Получаем текстовое значение статуса из choices
        status_display = dict(self.STATUS_CHOICES).get(self.status, "Неизвестный статус")
        # Форматируем дату создания без времени
        created_at_str = self.created_at.strftime("%d.%m.%Y")
        # Возвращаем строковое представление
        return f"Анкета от {created_at_str}, {self.last_name}, статус: {status_display}"

    
    
    # Метод для отображения возраста в формате "годы, месяцы"
    def get_age_display(self):
        years = self.child_age_in_months // 12
        months = self.child_age_in_months % 12
        return f"{years} лет, {months} мес."

