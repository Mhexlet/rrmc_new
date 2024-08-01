from datetime import datetime

from django.contrib import admin
from django.utils.html import format_html

from .models import Article, ArticleFile, ArticleApprovalApplication
from django_summernote.admin import SummernoteModelAdmin
from MedProject.settings import BASE_URL


@admin.register(Article)
class ArticleAdmin(SummernoteModelAdmin):
    list_display = ['author', 'hidden', 'theme', 'title', 'short_text', 'created_at', 'approved_at', 'approved']
    summernote_fields = ('text',)
    readonly_fields = ['files']

    def short_text(self, obj):
        return obj.text[:50] + '...'

    def files(self, obj):
        html_string = '<ul>'
        for file in obj.get_files:
            url = f'{BASE_URL}/media/{file.file.name}'
            html_string += f"<li><a href='{url}' target='_blank'>{url}</a></li>"
        html_string += '</ul>'
        return format_html(html_string)

    def save_model(self, request, obj, form, change):
        if (not change or (change and 'approved' in form.changed_data)) and form.instance.approved:
            form.instance.approved_at = datetime.now()
            app = ArticleApprovalApplication.objects.filter(article__pk=form.instance.pk, response=False)
            if app.exists():
                app = app.last()
                app.treated = True
                app.response = True
                app.save()
        return super(ArticleAdmin, self).save_model(request, obj, form, change)

    short_text.short_description = 'Текст'
    files.short_description = 'Файлы'


@admin.register(ArticleFile)
class ArticleFileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ArticleFile._meta.get_fields()]


@admin.register(ArticleApprovalApplication)
class ArticleApprovalApplicationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ArticleApprovalApplication._meta.get_fields()]