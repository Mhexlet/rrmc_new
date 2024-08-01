import os
from datetime import datetime

from django.db import models
from django.dispatch import receiver

from MedProject.settings import BASE_DIR


class QuestionAnswer(models.Model):

    name = models.CharField(max_length=64, verbose_name='Имя задавшего вопрос')
    question = models.TextField(verbose_name='Вопрос')
    answer = models.TextField(blank=True, null=True, verbose_name='Ответ')
    treated = models.BooleanField(default=False, verbose_name='Обработано')
    approved = models.BooleanField(default=False, verbose_name='Одобрено')
    created_at = models.DateTimeField(auto_now=True, verbose_name="Когда задан")
    treated_at = models.DateTimeField(null=True, blank=True, verbose_name="Когда обработан")

    class Meta:
        verbose_name = 'Вопрос - ответ'
        verbose_name_plural = 'Вопросы - ответы'

    def __str__(self):
        return self.question


class Review(models.Model):

    name = models.CharField(max_length=64, verbose_name='Имя оставившего отзыв')
    text = models.TextField(verbose_name='Отзыв')
    treated = models.BooleanField(default=False, verbose_name='Обработано')
    approved = models.BooleanField(default=False, verbose_name='Одобрено')
    created_at = models.DateTimeField(auto_now=True, verbose_name="Когда оставлен")
    treated_at = models.DateTimeField(null=True, blank=True, verbose_name="Когда обработан")

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.name}: {self.text[0:20]}...'


class MainSliderImage(models.Model):

    name = models.CharField(max_length=128, null=True, verbose_name='Название')
    image = models.ImageField(upload_to='tmp/', verbose_name='Изображение')
    link = models.TextField(null=True, blank=True, verbose_name='Ссылка при клике (необязательно)')
    order = models.PositiveIntegerField(blank=True, null=True, verbose_name='Порядок вывода')

    class Meta:
        verbose_name = 'Слайд с главной'
        verbose_name_plural = 'Слайды с главной'

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return '-'


class Banner(models.Model):

    image = models.ImageField(upload_to='tmp/', verbose_name='Изображение')
    name = models.CharField(max_length=128, verbose_name='Название')
    link = models.TextField(verbose_name='Ссылка')

    class Meta:
        verbose_name = 'Логотип министерств со ссылкой в подвале'
        verbose_name_plural = 'Логотипы министерств со ссылкой в подвале'

    def __str__(self):
        return f'{self.name}'


class Application(models.Model):

    first_name = models.CharField(max_length=64, verbose_name='Имя')
    patronymic = models.CharField(max_length=64, verbose_name='Отчество')
    last_name = models.CharField(max_length=64, verbose_name='Фамилия')
    address = models.TextField(verbose_name='Адрес')
    email = models.EmailField(verbose_name='Электронная почта')
    phone_number = models.CharField(max_length=16, verbose_name='Номер телефона')
    text = models.TextField(verbose_name='Текст обращения')
    answer = models.TextField(null=True, blank=True, verbose_name='Ответ')
    answering = models.CharField(max_length=64, null=True, blank=True, verbose_name='Имя ответившего')
    treated = models.BooleanField(default=False, verbose_name='Обработано')

    class Meta:
        verbose_name = 'Заявка на консультацию'
        verbose_name_plural = 'Заявки на консультацию'

    def __str__(self):
        return f'{self.first_name}: {self.text[0:20]}...'


class Place(models.Model):

    src = models.TextField(verbose_name='Ссылка на карту')
    name = models.CharField(max_length=64, verbose_name='Название места')
    text = models.TextField(null=True, blank=True, verbose_name='Описание')
    order = models.PositiveIntegerField(blank=True, null=True, verbose_name='Порядок вывода')

    class Meta:
        verbose_name = 'Город из географии ранней помощи'
        verbose_name_plural = 'Города из географии ранней помощи'

    def __str__(self):
        return self.name

    @property
    def get_institutions(self):
        return self.institutions.select_related().order_by('name')


class Institution(models.Model):

    name = models.CharField(max_length=256, verbose_name='Название')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='institutions', verbose_name='Город')
    phone_number = models.CharField(max_length=16, verbose_name='Номер телефона')
    address = models.TextField(verbose_name='Адрес')
    link = models.TextField(null=True, blank=True, verbose_name='Ссылка')

    class Meta:
        verbose_name = 'Учреждение из географии ранней помощи'
        verbose_name_plural = 'Учреждение из географии ранней помощи'

    def __str__(self):
        return self.name


class News(models.Model):

    title = models.CharField(max_length=128, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержимое')
    image = models.ImageField(upload_to='tmp/', verbose_name='Изображение')
    date = models.DateTimeField(auto_now=True, verbose_name='Дата публикации')
    order = models.PositiveIntegerField(blank=True, null=True, verbose_name='Порядок вывода')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title


class SiteContent(models.Model):

    name = models.CharField(unique=True, max_length=64, verbose_name='Название')
    content = models.TextField(verbose_name='Содержимое')

    class Meta:
        verbose_name = 'Наполнение сайта'
        verbose_name_plural = 'Наполнения сайта'

    def __str__(self):
        return self.name


class IndexLink(models.Model):

    image = models.ImageField(upload_to='tmp/', null=True, blank=True, verbose_name='Изображение')
    name = models.CharField(max_length=64, verbose_name='Название')
    link = models.TextField(verbose_name='Ссылка')

    class Meta:
        verbose_name = 'Горячая ссылка'
        verbose_name_plural = 'Горячие ссылки'

    def __str__(self):
        return self.name


@receiver(models.signals.pre_save, sender=QuestionAnswer)
def treat_question(sender, instance, raw, using, update_fields, *args, **kwargs):
    if instance.answer or instance.approved:
        instance.treated = True
    if instance.treated:
        instance.treated_at = datetime.now()


@receiver(models.signals.pre_save, sender=Review)
def treat_review(sender, instance, raw, using, update_fields, *args, **kwargs):
    if instance.approved:
        instance.treated = True
    if instance.treated:
        instance.treated_at = datetime.now()


@receiver(models.signals.pre_save, sender=Application)
def treat_application(sender, instance, raw, using, update_fields, *args, **kwargs):
    if instance.answer or instance.answering:
        instance.treated = True


@receiver(models.signals.pre_delete, sender=MainSliderImage)
def delete_slider_img(sender, instance, using, origin, **kwargs):
    try:
        os.remove(os.path.join(BASE_DIR, 'media', instance.image.name))
    except (FileNotFoundError, UnicodeEncodeError):
        pass


@receiver(models.signals.pre_delete, sender=Banner)
def delete_banner_img(sender, instance, using, origin, **kwargs):
    try:
        os.remove(os.path.join(BASE_DIR, 'media', instance.image.name))
    except (FileNotFoundError, UnicodeEncodeError):
        pass


@receiver(models.signals.pre_delete, sender=News)
def delete_news_img(sender, instance, using, origin, **kwargs):
    try:
        os.remove(os.path.join(BASE_DIR, 'media', instance.image.name))
    except (FileNotFoundError, UnicodeEncodeError):
        pass