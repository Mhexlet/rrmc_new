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

Перепробовано три итерации, рабочая — третья:

**Итерация 1 (не сработала):** `hashchange`-листенер + `history.replaceState`.
Причина: Google CSE добавляет хэш не через `location.hash =`, а через `history`-API,
которое **не триггерит** событие `hashchange`.

**Итерация 2 (не сработала):** Перехват `history.pushState` с отбросом
вызовов, содержащих `gsc.tab`. Причина: CSE использует другой метод
(скорее всего `replaceState` или прямой `Location.hash` сеттер).

**Итерация 3 (рабочая):** Защита по всем фронтам, инлайн-скрипт поднят
**выше** `cse.js` в `<head>`, чтобы патчи применились до загрузки CSE:

```javascript
(function() {
    var _push = history.pushState;
    var _replace = history.replaceState;
    history.pushState = function(state, title, url) {
        if (url && String(url).indexOf('gsc.tab') !== -1) return;
        return _push.apply(this, arguments);
    };
    history.replaceState = function(state, title, url) {
        if (url && String(url).indexOf('gsc.tab') !== -1) return;
        return _replace.apply(this, arguments);
    };
    try {
        var d = Object.getOwnPropertyDescriptor(Location.prototype, 'hash');
        if (d && d.set) {
            Object.defineProperty(Location.prototype, 'hash', {
                configurable: true,
                get: d.get,
                set: function(v) { if (String(v).indexOf('gsc.tab') !== -1) return; return d.set.call(this, v); }
            });
        }
    } catch(e) {}
    window.addEventListener('hashchange', function() {
        if (location.hash.indexOf('gsc.tab') !== -1) {
            _replace.call(history, null, document.title, location.pathname + location.search);
        }
    });
})();
```

Что делает:
- Патчит `history.pushState` и `history.replaceState` — отбрасывает вызовы с `gsc.tab` в URL
- Переопределяет сеттер `Location.prototype.hash` — игнорирует присваивания с `gsc.tab`
- Страхует `hashchange`-листенером — если что-то прорвётся, чистит через сохранённый оригинал `replaceState`

Проверено в Playwright: на главной и на `/single_news/310/` хэш не появляется ни сразу после загрузки, ни через 3 секунды.

## Затронутые файлы

- `static/css/style.scss` — исходник SCSS, два правила для `img`
- `static/css/style.css` — скомпилированный CSS (sass, force-added в git т.к. `static/` в .gitignore, sass отсутствует на сервере)
- `assets/css/styles.css` — Tailwind-исходник, синхронизирован с теми же правилами
- `main/templates/main/base.html` — скрипт удаления `#gsc.tab=0`

## Решение по деплою CSS

`static/` находится в `.gitignore`, sass на продакшн-сервере не установлен. Для деплоя `style.css` через git: скомпилирован локально, добавлен принудительно (`git add -f`). При будущих правках SCSS — та же схема.
