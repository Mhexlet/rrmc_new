import calendar
import os
import re
import time
from PIL import Image, ImageOps
from uuid import uuid4

from django.db import models
from django.dispatch import receiver
from translate import Translator
import secrets
from MedProject.settings import BASE_DIR


class Section(models.Model):

    name = models.CharField(max_length=64, verbose_name='Название раздела')
    order = models.PositiveSmallIntegerField(null=True, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'

    def __str__(self):
        return self.name

    @property
    def get_pages(self):
        return self.pages.select_related()


class Page(models.Model):

    title = models.CharField(max_length=100, unique=True, verbose_name='Заголовок страницы')
    url = models.CharField(max_length=128, unique=True, blank=True, verbose_name='URL страницы (заполняется автоматически)')
    section = models.ForeignKey(Section, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Раздел меню (оставьте незаполненным, если страница не является подразделом)', related_name='pages')
    content = models.TextField(verbose_name='Содержимое')
    approved = models.BooleanField(default=False, verbose_name='Публичный доступ')

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'

    def __str__(self):
        return self.title


# class PageBlock(models.Model):
#
#     TYPES = (
#         ('text', 'Текст'),
#         ('image', 'Изображение'),
#         ('map', 'Карта'),
#         ('html', 'HTML код'),
#         ('album', 'Альбом'),
#         ('file_set', 'Набор файлов'),
#     )
#
#     page = models.ForeignKey(Page, on_delete=models.CASCADE, verbose_name='Страница')
#     order = models.SmallIntegerField(verbose_name='Порядковый номер блока на странице')
#     type = models.CharField(max_length=32, choices=TYPES, verbose_name='Тип блока')


# class TextBlock(PageBlock):
#
#     text = models.TextField(verbose_name='Текст')
#
#
# class ImageBlock(PageBlock):
#
#     image = models.ImageField(upload_to='images/', verbose_name='Изображение')
#     name = models.CharField(max_length=128, null=True, blank=True, verbose_name='Подпись (необязательно)')
#
#
# class MapBlock(PageBlock):
#
#     src = models.TextField(verbose_name='Ссылка на карту')
#     name = models.CharField(max_length=128, null=True, blank=True, verbose_name='Подпись (необязательно)')


# class HTMLBlock(PageBlock):
#
#     html = models.TextField(verbose_name='HTML код')


class AlbumBlock(models.Model):

    page = models.ForeignKey(Page, on_delete=models.CASCADE, verbose_name='Страница')
    name = models.CharField(max_length=64, null=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'

    @property
    def get_images(self):
        return self.images.select_related()

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return '-'


class FileSetBlock(models.Model):

    page = models.ForeignKey(Page, on_delete=models.CASCADE, verbose_name='Страница')
    name = models.CharField(max_length=64, null=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Набор файлов'
        verbose_name_plural = 'Наборы файлов'

    @property
    def get_files(self):
        return self.files.select_related()

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return '-'


class AlbumImage(models.Model):

    image = models.ImageField(upload_to='tmp/', verbose_name='Изображение')
    album = models.ForeignKey(AlbumBlock, on_delete=models.CASCADE, null=True, related_name='images', verbose_name='Альбом')
    name = models.CharField(max_length=128, null=True, blank=True, verbose_name='Название (необязательно)')

    class Meta:
        verbose_name = 'Изображение из альбома'
        verbose_name_plural = 'Изображения из альбомов'

    def __str__(self):
        return self.image.name


class FileSetFile(models.Model):

    file = models.FileField(upload_to='documents/', verbose_name='Файл')
    file_set = models.ForeignKey(FileSetBlock, on_delete=models.CASCADE, null=True, related_name='files', verbose_name='Набор файлов')
    name = models.CharField(max_length=128, null=True, blank=True, verbose_name='Название (необязательно)')

    class Meta:
        verbose_name = 'Файл из набора'
        verbose_name_plural = 'Файлы из наборов'

    def __str__(self):
        return self.file.name

    @property
    def extension(self):
        name, ext = os.path.splitext(self.file.name)
        return ext


@receiver(models.signals.pre_save, sender=Page)
def add_url(sender, instance, raw, using, update_fields, *args, **kwargs):
    if not instance.url:
        translator = Translator(to_lang='en', from_lang='ru')
        title = re.sub(r'[!@#&()–\[{}\]:;\',?/*`~$^+=<>“]+', '', instance.title)
        title_list = title.split(' ')
        if len(title) > 3:
            title = ' '.join(title_list[0:3])
        url = translator.translate(title).replace(' ', '_')
        if Page.objects.filter(url=url).exists():
            url += secrets.token_urlsafe(5)
        instance.url = url.lower()


@receiver(models.signals.pre_save, sender=AlbumImage)
def compress_album_image(sender, instance, **kwargs):
    file = instance.image
    img = Image.open(file)
    img = ImageOps.exif_transpose(img)
    current_gmt = time.gmtime()
    time_stamp = calendar.timegm(current_gmt)
    file_name = f'{time_stamp}-{uuid4().hex}.jpg'
    new_file_path = os.path.join(BASE_DIR, 'media', 'images', file_name)
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
    instance.image = f'images/{file_name}'


@receiver(models.signals.pre_delete, sender=AlbumImage)
def delete_album_img(sender, instance, using, origin, **kwargs):
    try:
        os.remove(os.path.join(BASE_DIR, 'media', instance.image.name))
    except (FileNotFoundError, UnicodeEncodeError):
        pass


@receiver(models.signals.pre_delete, sender=FileSetFile)
def delete_file(sender, instance, using, origin, **kwargs):
    try:
        os.remove(os.path.join(BASE_DIR, 'media', instance.file.name))
    except (FileNotFoundError, UnicodeEncodeError):
        pass