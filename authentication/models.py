import os
import re
import shutil

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from datetime import datetime, timedelta
import pytz
from django_summernote.models import Attachment
from PIL import Image, ImageOps
from MedProject.settings import BASE_DIR, BASE_URL
from django.conf import settings
from main.models import SiteContent
import calendar
import time
from uuid import uuid4


def compress_img(instance, field, directory, multiple=True, change_format=True):
    file = getattr(instance, field)
    img = Image.open(file)
    img = ImageOps.exif_transpose(img)
    current_gmt = time.gmtime()
    time_stamp = calendar.timegm(current_gmt)
    file_name = f'{time_stamp}-{uuid4().hex}.{"jpg" if change_format else file.name.split(".")[-1]}'
    new_file_path = os.path.join(BASE_DIR, 'media', directory, file_name)
    width = img.size[0]
    height = img.size[1]
    ratio = width / height
    if ratio > 1 and width > 1024:
        sizes = [1024, int(1024 / ratio)]
        img = img.resize(sizes)
    elif height > 1024:
        sizes = [int(1024 * ratio), 1024]
        img = img.resize(sizes)
    try:
        img.save(new_file_path, quality=90, optimize=True)
    except OSError:
        img = img.convert("RGB")
        img.save(new_file_path, quality=90, optimize=True)
    if multiple:
        try:
            shutil.rmtree(os.path.join(BASE_DIR, 'media', 'tmp'))
        except (FileNotFoundError, PermissionError):
            pass
        os.mkdir(os.path.join(BASE_DIR, 'media', 'tmp'))
    setattr(instance, field, os.path.join(directory, file_name))


def user_photo_upload(instance, filename):
    current_gmt = time.gmtime()
    time_stamp = calendar.timegm(current_gmt)
    file_name = f'{time_stamp}-{uuid4().hex}.jpg'
    new_file_path = os.path.join(BASE_DIR, 'media', 'profile_photos', file_name)
    return new_file_path


class FieldOfActivity(models.Model):

    name = models.CharField(max_length=64, verbose_name='Название')

    class Meta:
        verbose_name = 'Сфера деятельности'
        verbose_name_plural = 'Сферы деятельности'

    def __str__(self):
        return self.name


class User(AbstractUser):

    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=64, verbose_name='Имя')
    patronymic = models.CharField(max_length=64, verbose_name='Отчество')
    last_name = models.CharField(max_length=64, verbose_name='Фамилия')
    # field_of_activity = models.ForeignKey(FieldOfActivity, on_delete=models.SET_NULL, null=True, verbose_name='Сфера деятельности')
    profession = models.CharField(max_length=64, verbose_name='Специализация')
    photo = models.ImageField(upload_to=user_photo_upload, verbose_name='Фото')
    city = models.CharField(max_length=128, verbose_name='Город')
    birthdate = models.DateField(null=True, verbose_name='Дата рождения')
    workplace_address = models.CharField(max_length=128, verbose_name='Адрес места работы')
    workplace_name = models.CharField(max_length=128, verbose_name='Название места работы')
    phone_number = models.CharField(max_length=16, verbose_name='Номер рабочего телефона')
    description = models.TextField(verbose_name='О себе')
    registered = models.BooleanField(default=False, verbose_name='Реестровый специалист')
    approved = models.BooleanField(default=False, verbose_name='Одобрен')
    email_verified = models.BooleanField(default=True, verbose_name='Почта подтверждена')
    verification_key = models.CharField(max_length=128, blank=True, null=True, verbose_name='Ключ подтверждения почты')
    verification_key_expires = models.DateTimeField(blank=True, null=True, verbose_name='Ключ истекает')
    order = models.PositiveIntegerField(blank=True, null=True, verbose_name='Порядок вывода')

    class Meta:
        verbose_name = 'Специалист ранней помощи'
        verbose_name_plural = 'Специалисты ранней помощи'

    @property
    def get_articles_count(self):
        return len(self.articles.select_related().filter(approved=True))

    @property
    def get_articles(self):
        return self.articles.select_related().filter(approved=True).order_by('-pk')

    @property
    def get_open_articles(self):
        return self.articles.select_related().filter(approved=True, hidden=False).order_by('-pk')

    @property
    def get_applications(self):
        return self.approval_applications.select_related().order_by('-pk')

    @property
    def get_waiting_edits(self):
        return self.edit_applications.select_related().filter(treated=False).order_by('-pk')

    @property
    def get_rejected_edits(self):
        return self.edit_applications.select_related().filter(treated=True, response=False).order_by('-pk')

    @property
    def get_birthdate(self):
        return self.birthdate.strftime("%d-%m-%Y")

    @property
    def application_exists(self):
        return UserApprovalApplication.objects.filter(user__pk=self.pk, treated=False).exists()

    @property
    def is_verification_key_expired(self):
        if datetime.now(pytz.timezone(settings.TIME_ZONE)) > self.verification_key_expires + timedelta(hours=48):
            return True
        return False

    @property
    def fields_of_activity(self):
        fields = self.fields.select_related()
        return ', '.join([str(field) for field in fields])

    @property
    def fields_of_activity_list(self):
        return self.fields.select_related()

    def __str__(self):
        try:
            return f'{self.last_name} {str(self.first_name)[0]}. {str(self.patronymic)[0]}.'
        except IndexError:
            return self.username




class FoAUserConnection(models.Model):

    foa = models.ForeignKey(FieldOfActivity, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Сфера деятельности')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fields', verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Сфера деятельности пользователей'
        verbose_name_plural = 'Сферы деятельности пользователей'

    def __str__(self):
        return str(self.foa)


class UserApprovalApplication(models.Model):

    user = models.ForeignKey(User, related_name='approval_applications', on_delete=models.CASCADE, verbose_name='Специалист')
    time = models.DateTimeField(auto_now=True, verbose_name='Время создания')
    treated = models.BooleanField(default=False, verbose_name='Обработана')
    response = models.BooleanField(default=False, verbose_name='Одобрить')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Заявка на одобрение профиля'
        verbose_name_plural = 'Заявки на одобрение профиля'

    def __str__(self):
        return f'{self.user}'


class UserEditApplication(models.Model):

    user = models.ForeignKey(User, related_name='edit_applications', on_delete=models.CASCADE, verbose_name='Специалист')
    field = models.CharField(max_length=32, verbose_name='Поле')
    verbose_field = models.CharField(max_length=32, null=True, verbose_name='Поле')
    old_value = models.TextField(verbose_name='Старое значение')
    new_value = models.TextField(verbose_name='Новое значение')
    time = models.DateTimeField(auto_now=True, verbose_name='Время создания')
    treated = models.BooleanField(default=False, verbose_name='Обработана')
    response = models.BooleanField(default=False, verbose_name='Одобрить')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Заявка на изменение профиля'
        verbose_name_plural = 'Заявки на изменение профиля'

    def __str__(self):
        return f'{self.user} - {self.field}'

    @property
    def get_value(self):
        if self.field == 'field_of_activity':
            result = re.sub(r'id:[0-9]+\|', '', str(self.new_value))
            result = re.sub(r'\|', ', ', result)
            return result[:-2]
        else:
            return self.new_value


@receiver(models.signals.pre_save, sender=User)
def compress_user_photo(sender, instance, raw, using, update_fields, *args, **kwargs):
    if not instance.pk:
        compress_img(instance, 'photo', 'profile_photos')


@receiver(models.signals.pre_save, sender=UserApprovalApplication)
def approve_user(sender, instance, raw, using, update_fields, *args, **kwargs):
    if instance.response:
        instance.user.approved = True
        instance.user.approved_at = datetime.now()
        instance.user.save()
        if not BASE_URL == 'http://127.0.0.1:8000':
            message = f'{SiteContent.objects.get(name="email_approved_text").content}'
            send_mail(
                'Ваш профиль одобрен',
                message,
                settings.EMAIL_HOST_USER,
                [instance.user.email],
                fail_silently=False
            )
    if instance.response or instance.comment:
        instance.treated = True


@receiver(models.signals.pre_save, sender=UserEditApplication)
def approve_edit(sender, instance, raw, using, update_fields, *args, **kwargs):
    if instance.response:
        if instance.field == 'field_of_activity':
            FoAUserConnection.objects.filter(user__pk=instance.user.pk).delete()
            for value in re.findall(r'id:[0-9]+\|', instance.new_value):
                new_value = int(value[3:-1])
                try:
                    foa = FieldOfActivity.objects.get(pk=new_value)
                    FoAUserConnection.objects.create(foa=foa, user=instance.user)
                except ObjectDoesNotExist:
                    pass
        elif instance.field == 'photo':
            try:
                os.remove(os.path.join(BASE_DIR, 'media', instance.user.photo.name))
            except (FileNotFoundError, UnicodeEncodeError):
                pass
            instance.user.photo = instance.new_value
        # elif instance.field == 'birthdate':
        #     instance.user.birthdate = f'{instance.new_value[6:]}-{instance.new_value[3:5]}-{instance.new_value[:2]}'
        else:
            setattr(instance.user, instance.field, instance.new_value)
        instance.user.save()
    if instance.response or instance.comment:
        instance.treated = True


@receiver(models.signals.pre_delete, sender=User)
def delete_user_photo(sender, instance, using, origin, **kwargs):
    try:
        os.remove(os.path.join(BASE_DIR, 'media', instance.photo.name))
    except (FileNotFoundError, UnicodeEncodeError):
        pass


@receiver(models.signals.pre_save, sender=Attachment)
def compress_attachment(sender, instance, **kwargs):
    file = instance.file.name
    ext = f'.{file.split(".")[-1]}'
    exts = Image.registered_extensions()
    supported_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}
    if ext in supported_extensions:
        img = Image.open(instance.file)
        img = ImageOps.exif_transpose(img)
        current_gmt = time.gmtime()
        time_stamp = calendar.timegm(current_gmt)
        file_name = f'{time_stamp}-{uuid4().hex}.jpg'
        new_file_path = os.path.join(BASE_DIR, 'media', 'attachments', file_name)
        width = img.size[0]
        height = img.size[1]
        ratio = width / height
        if ratio > 1 and width > 1024:
            sizes = [1024, int(1024 / ratio)]
            img = img.resize(sizes)
        elif height > 1024:
            sizes = [int(1024 * ratio), 1024]
            img = img.resize(sizes)
        try:
            img.save(new_file_path, quality=90, optimize=True)
        except OSError:
            img = img.convert("RGB")
            img.save(new_file_path, quality=90, optimize=True)
        instance.file = f'attachments/{file_name}'
