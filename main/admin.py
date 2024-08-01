import os
import re
import shutil

from django.contrib import admin

from MedProject.settings import BASE_DIR
from authentication.models import compress_img
from .models import QuestionAnswer, Review, MainSliderImage, Application, Place, News, SiteContent, Banner, IndexLink, \
    Institution
from django_summernote.admin import SummernoteModelAdmin


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_question', 'short_answer', 'treated', 'approved']
    readonly_fields = ('created_at',)

    def short_question(self, obj):
        return obj.question[:50] + '...'

    short_question.short_description = 'Вопрос'

    def short_answer(self, obj):
        if obj.answer is not None:
            return obj.answer[:50] + '...'
        return obj.answer

    short_answer.short_description = 'Ответ'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [field.name if field.name != 'text' else 'short_text' for field in Review._meta.get_fields()]
    readonly_fields = ('created_at',)

    def short_text(self, obj):
        return obj.text[:50] + '...'

    short_text.short_description = 'Текст'


@admin.register(MainSliderImage)
class MainSliderImageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MainSliderImage._meta.get_fields()]
    list_display_links = ('id', 'name',)

    def save_model(self, request, obj, form, change):
        if not change or (change and 'image' in form.changed_data):
            if change:
                try:
                    os.remove(os.path.join(BASE_DIR, 'media', form.initial['image'].name))
                except (FileNotFoundError, UnicodeEncodeError):
                    pass
            compress_img(form.instance, 'image', 'images')
        return super(MainSliderImageAdmin, self).save_model(request, obj, form, change)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Banner._meta.get_fields()]

    def save_model(self, request, obj, form, change):
        if not change or (change and 'image' in form.changed_data):
            if change:
                try:
                    os.remove(os.path.join(BASE_DIR, 'media', form.initial['image'].name))
                except (FileNotFoundError, UnicodeEncodeError):
                    pass
            compress_img(form.instance, 'image', 'images', change_format=False)
        return super(BannerAdmin, self).save_model(request, obj, form, change)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [field.name if field.name != 'text' else 'short_text' for field in Application._meta.get_fields()]

    def short_text(self, obj):
        return obj.text[:50] + '...'

    short_text.short_description = 'Текст обращения'


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'order', 'src']
    list_display_links = ('id', 'name',)

    def save_model(self, request, obj, form, change):
        if obj.src.startswith('<'):
            obj.src = re.search(r'src="[^ ]+', obj.src).group(0)[5:-1]
        obj.save()
        return super().save_model(request, obj, form, change)


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Institution._meta.get_fields()]

    def save_model(self, request, obj, form, change):
        if obj.link and not obj.link.startswith('http'):
            obj.link = f'http://{obj.link}'
        obj.save()
        return super().save_model(request, obj, form, change)


@admin.register(News)
class NewsAdmin(SummernoteModelAdmin):
    list_display = ['id', 'title', 'image', 'date']
    summernote_fields = ('content',)
    list_display_links = ('id', 'title',)

    def save_model(self, request, obj, form, change):
        if not change or (change and 'image' in form.changed_data):
            if change:
                try:
                    os.remove(os.path.join(BASE_DIR, 'media', form.initial['image'].name))
                except (FileNotFoundError, UnicodeEncodeError):
                    pass
            compress_img(form.instance, 'image', 'images')
        try:
            shutil.rmtree(os.path.join(BASE_DIR, 'media', 'django-summernote'))
        except (FileNotFoundError, PermissionError):
            pass
        return super(NewsAdmin, self).save_model(request, obj, form, change)


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SiteContent._meta.get_fields()]
    readonly_fields = ['name']

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(IndexLink)
class IndexLinkAdmin(admin.ModelAdmin):
    list_display = [field.name for field in IndexLink._meta.get_fields()]

    def save_model(self, request, obj, form, change):
        if not change or (change and 'image' in form.changed_data):
            if change:
                try:
                    os.remove(os.path.join(BASE_DIR, 'media', form.initial['image'].name))
                except (FileNotFoundError, UnicodeEncodeError):
                    pass
            compress_img(form.instance, 'image', 'images', change_format=False)
        return super(IndexLinkAdmin, self).save_model(request, obj, form, change)
