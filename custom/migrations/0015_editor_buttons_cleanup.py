"""
Разовая чистка кнопок, сделанных по-старому.

Раньше кнопки вставлялись HTML-сниппетом: <style>.btn {...}</style> + <a class="btn">.
CKEditor 5 при сохранении выкидывает класс btn, а <style> превращает в абзац
с CSS-текстом. Здесь убираем этот мусор и переводим ссылки на новый класс
rr-btn, который ставит переключатель «Кнопка» в редакторе.

Логика скопирована, а не импортирована из main.editor_content, чтобы миграция
не менялась вместе с кодом приложения. Повторный запуск ничего не меняет.
"""
import html
import re

from django.db import migrations

# У <meta> обязателен пробел после имени: на странице useful_information есть битый
# <img ... <meta="" charset="utf-8">, и без пробела регулярка съела бы конец тега img
DOCUMENT_TAGS = re.compile(r'<(style|title)\b[^>]*>.*?</\1\s*>|<meta\s[^>]*>', re.I | re.S)
PARAGRAPH = re.compile(r'<p\b[^>]*>(.*?)</p>', re.I | re.S)
TAG = re.compile(r'<[^>]+>')
CSS_TEXT = re.compile(r'(?:[.#@*a-zA-Z][^{}]{0,200}\{[^{}]*?[-a-zA-Z]+\s*:[^{};]*;[^{}]*\}\s*)+', re.S)
# Пустые «ссылки» без href, в атрибуты которых при вставке попал CSS (страница «Аттестация»)
JUNK_LINK = re.compile(r'<a\s(?![^>]*\bhref=)[^>]*>\s*</a>', re.I)
OLD_BUTTON_CLASS = re.compile(r'(<a\b[^>]*\bclass=")btn(")', re.I)

# На этой странице кнопка «Подать заявку» уже потеряла класс при сохранении в CKEditor 5.
# В старом стиле она стояла по центру (display: block; margin: 0 auto).
LOST_BUTTON_PAGE = 'useful_information_for_specialists'
LOST_BUTTON_OLD = '<p><a href="https://reestr.eii.ru/">'
LOST_BUTTON_NEW = '<p style="text-align:center;"><a class="rr-btn" href="https://reestr.eii.ru/">'


def _looks_like_css(fragment):
    text = html.unescape(TAG.sub('', fragment)).replace('\xa0', ' ').strip()
    return bool(text) and CSS_TEXT.fullmatch(text) is not None


def clean(content):
    content = DOCUMENT_TAGS.sub('', content)
    content = PARAGRAPH.sub(lambda m: '' if _looks_like_css(m.group(1)) else m.group(0), content)
    content = JUNK_LINK.sub('', content)
    return OLD_BUTTON_CLASS.sub(r'\1rr-btn\2', content)


def cleanup_buttons(apps, schema_editor):
    Page = apps.get_model('custom', 'Page')
    for page in Page.objects.all():
        content = clean(page.content or '')
        if page.url == LOST_BUTTON_PAGE:
            content = content.replace(LOST_BUTTON_OLD, LOST_BUTTON_NEW)
        if content != page.content:
            page.content = content
            page.save(update_fields=['content'])


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0014_import_collective_members'),
    ]

    operations = [
        migrations.RunPython(cleanup_buttons, migrations.RunPython.noop),
    ]
