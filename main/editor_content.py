"""
Защита полей CKEditor от вставленного CSS.

Заказчица раньше делала кнопки по рецепту из интернета: блок <style>.btn {...}</style>
плюс ссылка с class="btn". CKEditor 5 так не умеет: <style> он превращает в абзац,
и CSS-код показывается на сайте обычным текстом. Теперь кнопки делаются
переключателем «Кнопка» в свойствах ссылки, а этот модуль вычищает остатки
старого способа при сохранении и объясняет в админке, как надо.
"""
import html
import re

from django.contrib import messages

# <style> и <title> вместе с содержимым, <meta ...> — куски вставленных HTML-документов.
# У <meta> обязателен пробел после имени: в старом контенте встречается битый
# <img ... <meta="" charset="utf-8">, и без пробела регулярка съела бы конец тега img.
_DOCUMENT_TAGS = re.compile(r'<(style|title)\b[^>]*>.*?</\1\s*>|<meta\s[^>]*>', re.I | re.S)

_PARAGRAPH = re.compile(r'<p\b[^>]*>(.*?)</p>', re.I | re.S)
_TAG = re.compile(r'<[^>]+>')
# Одно или несколько CSS-правил вида ".btn { display: block; ... }": селектор
# начинается с латиницы или .#@*, внутри скобок есть хотя бы одно «свойство: значение;»
_CSS_TEXT = re.compile(r'(?:[.#@*a-zA-Z][^{}]{0,200}\{[^{}]*?[-a-zA-Z]+\s*:[^{};]*;[^{}]*\}\s*)+', re.S)


def _looks_like_css(fragment):
    text = html.unescape(_TAG.sub('', fragment)).replace('\xa0', ' ').strip()
    return bool(text) and _CSS_TEXT.fullmatch(text) is not None


def clean_editor_html(content):
    """Возвращает (очищенный HTML, найден ли и удалён вставленный CSS)."""
    cleaned = _DOCUMENT_TAGS.sub('', content)
    cleaned = _PARAGRAPH.sub(lambda m: '' if _looks_like_css(m.group(1)) else m.group(0), cleaned)
    return cleaned, cleaned != content


EDITOR_HELP_TEXT = (
    '<b>Кнопка:</b> выделите текст → «Ссылка» (или Ctrl+K) → вставьте адрес → нажмите на ссылку → '
    '«Свойства ссылки» (значок с ползунками) → включите «Кнопка». '
    '<b>Размер и цвет:</b> нажмите на кнопку → «Стили» в появившейся панели. '
    'Выравнивание — обычными кнопками выравнивания текста.<br>'
    '<b>Плашки и крупный текст:</b> поставьте курсор в абзац → «Стили» на верхней панели редактора.<br>'
    'Вставлять CSS-код и &lt;style&gt; не нужно: такой код удаляется при сохранении.'
)


class EditorContentAdminMixin:
    """
    Для админок с CKEditor: подсказка под полем и чистка вставленного CSS
    при сохранении. Поля перечисляются в editor_fields.
    """
    editor_fields = ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield is not None and db_field.name in self.editor_fields:
            formfield.help_text = EDITOR_HELP_TEXT
        return formfield

    def save_model(self, request, obj, form, change):
        removed_css = False
        for field in self.editor_fields:
            cleaned, removed = clean_editor_html(getattr(obj, field) or '')
            if removed:
                setattr(obj, field, cleaned)
                removed_css = True
        if removed_css:
            messages.warning(
                request,
                'Из текста убран вставленный CSS-код — на сайте он показывался бы как обычный текст. '
                'Кнопку можно сделать так: нажмите на ссылку → «Свойства ссылки» → «Кнопка».',
            )
        super().save_model(request, obj, form, change)
