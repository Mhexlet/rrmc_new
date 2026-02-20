from django.db import models


class CookieConsentSettings(models.Model):
    """Настройки баннера cookie-уведомления."""

    message = models.TextField(
        verbose_name='Текст сообщения',
        default=(
            'На сайте используется сервис веб-аналитики Яндекс Метрика '
            'с помощью технологий cookie для сбора и хранения данных, '
            'необходимых для корректной работы сайта и удобства посетителей. '
            'Продолжая пользоваться сайтом, вы соглашаетесь с использованием '
            'файлов cookie и политикой конфиденциальности персональных данных.'
        ),
    )
    policy_url = models.CharField(
        max_length=255,
        verbose_name='Ссылка на политику конфиденциальности',
        default='/custom/personal_data/',
    )
    hide_days = models.PositiveIntegerField(
        verbose_name='Скрывать на (дней)',
        default=14,
    )

    class Meta:
        verbose_name = 'Настройки cookie-уведомления'
        verbose_name_plural = 'Настройки cookie-уведомления'

    def __str__(self):
        return 'Настройки cookie-уведомления'

    def save(self, *args, **kwargs):
        # Гарантируем единственную запись (singleton)
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
