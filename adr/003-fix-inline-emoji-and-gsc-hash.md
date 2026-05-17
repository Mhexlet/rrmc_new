# ADR-003: Фикс inline-эмодзи в контенте и удаление #gsc.tab=0 из URL

**Дата:** 2026-05-17  
**Статус:** Принято

## Контекст

Две визуальные проблемы в публичной части сайта:

1. **Смайлики из VK** (`<img width="16" height="16">` — встраиваемые эмодзи) отображались по центру на отдельной строке вместо inline рядом с текстом. Причина — два CSS-правила в `static/css/style.scss`:
   - `.news-news-content img` имел `margin: 10px auto`, что центрировало все `<img>`
   - `.news-news-content p:has(> img)` превращал любой `<p>` с `<img>` в flex-колонку, выталкивая эмодзи на новую строку

2. **`#gsc.tab=0` в URL** добавлялся скриптом Google Custom Search (`cse.google.com/cse.js`) при каждой загрузке страницы.

## Решение

### Проблема 1: Эмодзи

В `static/css/style.scss` добавлено правило-исключение для мелких картинок (16×16 px):

```css
.page-content img[width="16"], .news-news-content img[width="16"], .article-text img[width="16"],
.page-content img[height="16"], .news-news-content img[height="16"], .article-text img[height="16"] {
    display: inline;
    vertical-align: middle;
    margin: 0 2px;
    border-radius: 0;
    max-width: none;
}
```

Правило `p:has(> img)` сужено до `p:has(> img:not([width="16"]))` — flex-колонка применяется только к полноразмерным изображениям CKEditor (`<figure>`), не к inline-эмодзи.

### Проблема 2: #gsc.tab=0

В `main/templates/main/base.html` добавлен скрипт после подключения GSC:

```javascript
window.addEventListener('hashchange', function() {
    if (window.location.hash === '#gsc.tab=0') {
        history.replaceState(null, document.title, window.location.pathname + window.location.search);
    }
});
if (window.location.hash === '#gsc.tab=0') {
    history.replaceState(null, document.title, window.location.pathname + window.location.search);
}
```

## Затронутые файлы

- `static/css/style.scss` — исходник SCSS, два правила для `img`
- `static/css/style.css` — скомпилированный CSS (sass, force-added в git т.к. `static/` в .gitignore, sass отсутствует на сервере)
- `assets/css/styles.css` — Tailwind-исходник, синхронизирован с теми же правилами
- `main/templates/main/base.html` — скрипт удаления `#gsc.tab=0`

## Решение по деплою CSS

`static/` находится в `.gitignore`, sass на продакшн-сервере не установлен. Для деплоя `style.css` через git: скомпилирован локально, добавлен принудительно (`git add -f`). При будущих правках SCSS — та же схема.
