from django.db import models
import os
from datetime import datetime
from django.dispatch import receiver

from MedProject.settings import BASE_DIR
from authentication.models import User


class Article(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='Автор', related_name='articles')
    hidden = models.BooleanField(default=False, verbose_name='Статья скрыта')
    theme = models.TextField(verbose_name='Тематика')
    title = models.TextField(verbose_name='Название статьи')
    text = models.TextField(verbose_name='Текст статьи')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата написания')
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата публикации')
    approved = models.BooleanField(default=False, verbose_name='Одобрено')

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.title

    @property
    def get_files(self):
        return self.files.select_related()


class ArticleFile(models.Model):

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='documents/')
    name = models.CharField(max_length=128, null=True, blank=True, verbose_name='Название (необязательно)')

    class Meta:
        verbose_name = 'Файл из статьи'
        verbose_name_plural = 'Файлы из статей'

    @property
    def extension(self):
        name, ext = os.path.splitext(self.file.name)
        return ext


class ArticleApprovalApplication(models.Model):

    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Статья')
    time = models.DateTimeField(auto_now=True, verbose_name='Время создания')
    treated = models.BooleanField(default=False, verbose_name='Обработана')
    response = models.BooleanField(default=False, verbose_name='Опубликовать')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Заявка на публикацию статьи'
        verbose_name_plural = 'Заявки на публикацию статьи'

    def __str__(self):
        return f'{self.article}'


@receiver(models.signals.pre_save, sender=ArticleApprovalApplication)
def approve_article(sender, instance, raw, using, update_fields, *args, **kwargs):
    if instance.response:
        instance.article.approved = True
        instance.article.approved_at = datetime.now()
        instance.article.save()
    if instance.response or instance.comment:
        instance.treated = True


@receiver(models.signals.pre_delete, sender=ArticleFile)
def delete_file(sender, instance, using, origin, **kwargs):
    try:
        os.remove(os.path.join(BASE_DIR, 'media', instance.file.name))
    except (FileNotFoundError, UnicodeEncodeError):
        pass
