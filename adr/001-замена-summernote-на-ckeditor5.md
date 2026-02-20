# ADR-001: Замена django-summernote на django-ckeditor-5 в админке

**Дата:** 2026-02-20  
**Статус:** Принято  

## Контекст

В проекте для WYSIWYG-редактирования контента в админке Django использовался пакет `django-summernote==0.8.20.0`. Редактор морально устарел, интерфейс неудобный. Принято решение заменить на `django-ckeditor-5` — современный блочный редактор с drag&drop, таблицами, медиа и т.д.

## Область изменений

Замена касается ТОЛЬКО админской части (django admin). Фронтенд-шаблоны, где Summernote подключается через статические JS/CSS файлы (register.html, edit_profile.html, create_article_page.html, edit_article_page.html), НЕ затрагиваются — там используется standalone Summernote, не связанный с django-summernote пакетом.

## Затронутые файлы

### 1. requirements.txt
- **Было:** `django-summernote==0.8.20.0`
- **Стало:** `django-ckeditor-5>=0.2.15`

### 2. MedProject/settings.py
- Из `INSTALLED_APPS`: `'django_summernote'` → `'django_ckeditor_5'`
- Удалён блок `SUMMERNOTE_CONFIG`
- Добавлен блок `CKEDITOR_5_CONFIGS` и `CKEDITOR_5_FILE_STORAGE`

### 3. MedProject/settings_prod.py
- Аналогичные изменения что и в settings.py

### 4. MedProject/urls.py
- **Было:** `path('editor/', include('django_summernote.urls'))`
- **Стало:** `path('ckeditor5/', include('django_ckeditor_5.urls'))`

### 5. custom/admin.py (PageAdmin)
- **Было:** наследование от `SummernoteModelAdmin`, `summernote_fields = ('content',)`
- **Стало:** наследование от `admin.ModelAdmin`, использование `CKEditor5Widget` через `formfield_overrides`
- Удалена очистка папки `media/django-summernote` в `save_model`

### 6. main/admin.py (NewsAdmin)
- **Было:** наследование от `SummernoteModelAdmin`, `summernote_fields = ('content',)`
- **Стало:** наследование от `admin.ModelAdmin`, использование `CKEditor5Widget` через `formfield_overrides`
- Удалена очистка папки `media/django-summernote` в `save_model`

### 7. specialists/admin.py (ArticleAdmin)
- **Было:** наследование от `SummernoteModelAdmin`, `summernote_fields = ('text',)`
- **Стало:** наследование от `admin.ModelAdmin`, использование `CKEditor5Widget` через `formfield_overrides`

### 8. authentication/admin.py (UserAdmin)
- **Было:** наследование от `SummernoteModelAdmin`, `summernote_fields = ('description',)`
- **Стало:** наследование от `admin.ModelAdmin`, использование `CKEditor5Widget` через `formfield_overrides`

### 9. authentication/models.py
- **Было:** `from django_summernote.models import Attachment` и сигнал `compress_attachment` для сжатия вложений Summernote
- **Стало:** импорт и сигнал удалены (CKEditor 5 использует свой механизм загрузки файлов)

## Инструкция отката

Если нужно вернуть всё обратно:

### Шаг 1: Зависимости
```bash
pip uninstall django-ckeditor-5
pip install django-summernote==0.8.20.0
```

### Шаг 2: requirements.txt
Заменить `django-ckeditor-5>=0.2.15` обратно на `django-summernote==0.8.20.0`

### Шаг 3: settings.py и settings_prod.py
- В `INSTALLED_APPS`: `'django_ckeditor_5'` → `'django_summernote'`
- Удалить блоки `CKEDITOR_5_CONFIGS` и `CKEDITOR_5_FILE_STORAGE`
- Вернуть блок:
```python
SUMMERNOTE_CONFIG = {
    'attachment_filesize_limit': 30000000,
    'toolbar': [
        ['style', ['style']],
        ['font', ['bold', 'underline', 'clear']],
        ['fontname', ['fontname']],
        ['color', ['color']],
        ['para', ['ul', 'ol', 'paragraph']],
        ['table', ['table']],
        ['insert', ['link', 'picture']],
        ['view', ['fullscreen', 'codeview', 'help']],
    ],
}
```

### Шаг 4: urls.py
Заменить `path('ckeditor5/', include('django_ckeditor_5.urls'))` обратно на `path('editor/', include('django_summernote.urls'))`

### Шаг 5: admin.py файлы (custom, main, specialists, authentication)
Во всех четырёх файлах:
- Вернуть импорт: `from django_summernote.admin import SummernoteModelAdmin`
- Убрать импорт: `from django_ckeditor_5.widgets import CKEditor5Widget`
- Вернуть наследование от `SummernoteModelAdmin` вместо `admin.ModelAdmin`
- Вернуть `summernote_fields = (...)` вместо `formfield_overrides`
- В custom/admin.py и main/admin.py вернуть очистку папки django-summernote в save_model

### Шаг 6: authentication/models.py
Вернуть:
```python
from django_summernote.models import Attachment

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
```

### Шаг 7: Миграции
Миграции БД НЕ требуются ни для установки, ни для отката — тип полей в моделях (TextField) не менялся. Виджет CKEditor подключается только на уровне админки.
