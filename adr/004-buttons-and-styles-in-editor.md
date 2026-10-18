# ADR-004: Кнопки и плашки в редакторе вместо вставки HTML/CSS

**Дата:** 2026-10-18  
**Статус:** Принято

## Контекст

Заказчица делала кнопки на страницах HTML-сниппетом из интернета: блок `<style>.btn {...}</style>` и ссылка `<a class="btn">`. Summernote такое пропускал. CKEditor 5 (ADR-001) при сохранении убирает у ссылки класс `btn`, а содержимое `<style>` превращает в абзац, и на странице появляется CSS-код текстом. Так сломалась кнопка «Подать заявку» на `/custom/useful_information_for_specialists/`. Ещё 4 страницы (`blank_page`, `useful_information`, `certification`, `advanced_training_courses`) работали только потому, что их пока не пересохраняли в новом редакторе.

## Решение

Всё на плагинах, которые уже есть в сборке `django-ckeditor-5` (CKEditor 47.3.0). Свою сборку редактора не делаем.

1. **Переключатель «Кнопка»** в окне ссылки («Свойства ссылки») — ручной link decorator, ставит класс `rr-btn`. Рядом «Открывать в новой вкладке».
2. **Список «Стили»** (плагин Style, сам настраивает General HTML Support):
   - для ссылок: размеры (`rr-btn--sm`, `--lg`, `--wide`), контурная (`--outline`), 8 цветов (`--blue`, `--red`, …);
   - для абзацев: плашки «инфо / важно / совет» (`rr-note`), «Крупный текст» (`rr-lead`).
   «Стили» есть и на верхней панели, и во всплывающей панели ссылки (`link.toolbar`): при клике по кнопке размер и цвет выбираются прямо там. Во всплывающей панели группа стилей абзацев скрыта CSS-правилом в `editor-content.scss`, там остаются только кнопки.
   Стили ставят только модификаторы без `rr-btn`, иначе после повторного открытия страницы `rr-btn` забирает переключатель и стиль перестаёт подсвечиваться. Поэтому кнопкой на сайте считается и `a.rr-btn`, и `a[class*="rr-btn--"]`.
3. **Защита при сохранении** (`main/editor_content.py`, миксин для админок страниц, новостей и статей): вырезаются `<style>`, `<title>`, `<meta>` и абзацы, целиком состоящие из CSS-правил, и показывается предупреждение. Под полем редактора — короткая инструкция.
4. **Разовая чистка** — миграция `custom/0015_editor_buttons_cleanup`: убирает мусор старого способа, `class="btn"` → `class="rr-btn"`, возвращает кнопку «Подать заявку».
5. Интерфейс редактора переведён на русский (`language: ru`).

### Где что лежит

- `MedProject/ckeditor_config.py` — конфиг редактора, список цветов и размеров. `settings.py`/`settings_prod.py` не в git и только импортируют его.
- `static/css/_content-blocks.scss` — внешний вид кнопок и плашек. Подключается в `style.scss` (сайт) и в `editor-content.scss` (окно редактора в админке через `CKEDITOR_5_CUSTOM_CSS`), поэтому в редакторе кнопки выглядят как на сайте.
- Новый цвет кнопки добавляется в два места: `$rr-btn-colors` в `_content-blocks.scss` и `BUTTON_COLORS` в `ckeditor_config.py`.

## Деплой

`static/` в `.gitignore`, новые файлы добавлять через `git add -f`: `static/css/_content-blocks.scss`, `static/css/editor-content.scss`, `static/css/editor-content.css` (плюс как обычно `style.scss`, `style.css`).

Сборка CSS локально:

```bash
sass --style=compressed --no-source-map static/css/style.scss static/css/style.css
sass --style=compressed --no-source-map static/css/editor-content.scss static/css/editor-content.css
```

На сервере, кроме обычных шагов (pull, migrate, перезапуск PM2):

1. **Вручную** в `MedProject/settings.py` и `MedProject/settings_prod.py` заменить блок от `customColorPalette = [` до конца `CKEDITOR_5_CONFIGS` на
   ```python
   from MedProject.ckeditor_config import CKEDITOR_5_CONFIGS, CKEDITOR_5_CUSTOM_CSS  # noqa: E402
   ```
   Без этого редактор при сохранении будет снова срезать класс `rr-btn` с кнопок.
2. Скопировать оба CSS в каталог, из которого nginx отдаёт статику:
   ```bash
   cp static/css/style.css static/css/editor-content.css /var/www/static/css/
   ```

## Откат

Вернуть старый блок `CKEDITOR_5_CONFIGS` в настройки, убрать миксин из админок. При откате миграция 0015 ничего не делает (`RunPython.noop`): удалённые `<style>`-блоки не вернутся, а кнопки останутся обычными ссылками с классом `rr-btn`.
