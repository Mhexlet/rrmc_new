"""
Настройки CKEditor 5 для админки.

settings.py и settings_prod.py не лежат в git, поэтому конфиг редактора живёт
здесь, а настройки только импортируют его:

    from MedProject.ckeditor_config import CKEDITOR_5_CONFIGS, CKEDITOR_5_CUSTOM_CSS

Внешний вид кнопок и плашек описан в static/css/_content-blocks.scss: этот файл
входит и в стили сайта (style.scss), и в стили самого редактора (editor-content.scss),
поэтому в админке кнопка выглядит так же, как на сайте.
"""

# Цвета кнопок. Ключ — суффикс CSS-класса rr-btn--<ключ>, его же цвет задаёт
# $rr-btn-colors в _content-blocks.scss. Новый цвет добавляется в оба места.
BUTTON_COLORS = [
    ('blue', 'Синяя'),
    ('navy', 'Тёмно-синяя'),
    ('green', 'Зелёная'),
    ('orange', 'Оранжевая'),
    ('red', 'Красная'),
    ('pink', 'Розовая'),
    ('purple', 'Фиолетовая'),
    ('dark', 'Тёмная'),
]

# Названия короткие: в списке «Стили» под превью помещается ~15 символов,
# а то, что это кнопки, видно по самим превью
BUTTON_SIZES = [
    ('sm', 'Маленькая'),
    ('lg', 'Большая'),
    ('wide', 'Широкая'),
    ('outline', 'Контурная'),
]

# Базовый класс rr-btn ставит переключатель «Кнопка» в окне ссылки, а стили из
# списка «Стили» добавляют только модификаторы. Если положить rr-btn и в стили,
# после повторного открытия страницы его заберёт переключатель и стиль перестанет
# подсвечиваться в списке. Ссылка с любым модификатором на сайте тоже кнопка.
BUTTON_STYLES = [
    {'name': name, 'element': 'a', 'classes': [f'rr-btn--{key}']}
    for key, name in BUTTON_SIZES + BUTTON_COLORS
]

BLOCK_STYLES = [
    {'name': 'Плашка: инфо', 'element': 'p', 'classes': ['rr-note', 'rr-note--info']},
    {'name': 'Плашка: важно', 'element': 'p', 'classes': ['rr-note', 'rr-note--warning']},
    {'name': 'Плашка: совет', 'element': 'p', 'classes': ['rr-note', 'rr-note--success']},
    {'name': 'Крупный текст', 'element': 'p', 'classes': ['rr-lead']},
]

customColorPalette = [
    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
]

CKEDITOR_5_CONFIGS = {
    'default': {
        'language': 'ru',
        'toolbar': [
            'heading', 'style', '|',
            'bold', 'italic', 'underline', 'strikethrough', '|',
            'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|',
            'alignment', '|',
            'bulletedList', 'numberedList', 'todoList', '|',
            'outdent', 'indent', '|',
            'link', 'insertImage', 'mediaEmbed', 'insertTable', 'blockQuote', 'codeBlock', '|',
            'horizontalLine', 'sourceEditing', '|',
            'undo', 'redo',
        ],
        'link': {
            # «Стили» прямо во всплывающей панели ссылки: при клике по кнопке
            # размер и цвет выбираются там же, а не на верхней панели редактора
            'toolbar': ['linkPreview', '|', 'editLink', 'linkProperties', 'style', 'unlink'],
            'decorators': {
                'isButton': {
                    'mode': 'manual',
                    'label': 'Кнопка',
                    'classes': 'rr-btn',
                },
                'openInNewTab': {
                    'mode': 'manual',
                    'label': 'Открывать в новой вкладке',
                    'attributes': {'target': '_blank', 'rel': 'noopener noreferrer'},
                },
            },
        },
        'style': {
            'definitions': BUTTON_STYLES + BLOCK_STYLES,
        },
        'image': {
            'toolbar': [
                'imageTextAlternative', '|',
                'imageStyle:inline', 'imageStyle:block', 'imageStyle:side',
                'imageStyle:alignLeft', 'imageStyle:alignCenter', 'imageStyle:alignRight',
                '|', 'toggleImageCaption', '|',
                'imageResize',
            ],
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties'],
            'tableProperties': {'borderColors': customColorPalette, 'backgroundColors': customColorPalette},
            'tableCellProperties': {'borderColors': customColorPalette, 'backgroundColors': customColorPalette},
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
            ],
        },
        'list': {
            'properties': {
                'styles': True,
                'startIndex': True,
                'reversed': True,
            },
        },
    },
}

# Стили содержимого для окна редактора в админке (путь относительно STATIC_URL)
CKEDITOR_5_CUSTOM_CSS = 'css/editor-content.css'
