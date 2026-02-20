# ADR-001: Миграция Django с runserver на gunicorn

**Дата:** 2026-02-14  
**Сервер:** 92.63.102.115  
**Проект:** orc-rrmc.ru (Django 4.2.5)

## Контекст

Django-проект orc-rrmc.ru работал через `manage.py runserver 20000` — отладочный сервер, не предназначенный для продакшена. Процесс потреблял 390 МБ RAM на сервере с 965 МБ, swap был забит на 100%.

## Что было сделано

### 1. Очистка сервера

- Удалены неиспользуемые Docker-образы (`medproject`, `python:3.9`) — освобождено 1.3 ГБ
- Очищены журналы systemd (`journalctl --vacuum-size=100M`) — освобождено 1.8 ГБ
- Итого освобождено ~3.1 ГБ дискового пространства

### 2. Установка gunicorn

```bash
/var/www/www-root/data/www/orc-rrmc.ru/.venv/bin/pip install gunicorn
```

Установлен gunicorn 25.1.0 в существующий venv проекта.

### 3. Изменение конфигурации PM2

Файл: `/var/www/www-root/data/www/orc-rrmc.ru/ecosystem.config.js`

**Было:**
```js
module.exports = {
  "apps" : [{
    "args" : [ "runserver", "20000" ],
    "name" : "orc-rrmc.ru",
    "script" : "manage.py"
  }]
}
```

**Стало:**
```js
module.exports = {
  "apps" : [{
    "name" : "orc-rrmc.ru",
    "script" : "/var/www/www-root/data/www/orc-rrmc.ru/.venv/bin/gunicorn",
    "args" : "MedProject.wsgi:application --bind 127.0.0.1:20000 --workers 2 --timeout 30",
    "cwd" : "/var/www/www-root/data/www/orc-rrmc.ru",
    "interpreter" : "none"
  }]
}
```

Бэкап оригинала: `ecosystem.config.js.bak`

### 4. Результат

| Метрика            | runserver   | gunicorn       |
|--------------------|-------------|----------------|
| RAM used           | 629 МБ      | 391 МБ         |
| RAM available      | 171 МБ      | 408 МБ         |
| Swap used          | 228/228 МБ  | 162/228 МБ     |
| Django memory      | 390 МБ      | ~185 МБ        |

## Архитектура

```
Клиент → nginx (80/443) → proxy_pass → gunicorn (127.0.0.1:20000) → Django WSGI
                                         ↑
                                    PM2 управляет
                                         ↑
                              systemd (pm2-www-root.service)
```

## Управление Django/gunicorn

Все команды выполняются от root. PM2 сам запускает процесс от пользователя www-root.

### Статус
```bash
sudo -u www-root bash -c 'export HOME=/var/www/www-root/data && /usr/lib/ispnodejs/lib/node_modules/pm2/bin/pm2 list'
```

### Перезапуск
```bash
sudo -u www-root bash -c 'export HOME=/var/www/www-root/data && /usr/lib/ispnodejs/lib/node_modules/pm2/bin/pm2 restart orc-rrmc.ru'
```

### Остановка
```bash
sudo -u www-root bash -c 'export HOME=/var/www/www-root/data && /usr/lib/ispnodejs/lib/node_modules/pm2/bin/pm2 stop orc-rrmc.ru'
```

### Запуск (если остановлен)
```bash
sudo -u www-root bash -c 'export HOME=/var/www/www-root/data && /usr/lib/ispnodejs/lib/node_modules/pm2/bin/pm2 start orc-rrmc.ru'
```

### Логи
```bash
sudo -u www-root bash -c 'export HOME=/var/www/www-root/data && /usr/lib/ispnodejs/lib/node_modules/pm2/bin/pm2 logs orc-rrmc.ru --lines 50'
```

### После изменения ecosystem.config.js
```bash
sudo -u www-root bash -c 'export HOME=/var/www/www-root/data && /usr/lib/ispnodejs/lib/node_modules/pm2/bin/pm2 delete orc-rrmc.ru && /usr/lib/ispnodejs/lib/node_modules/pm2/bin/pm2 start /var/www/www-root/data/www/orc-rrmc.ru/ecosystem.config.js && /usr/lib/ispnodejs/lib/node_modules/pm2/bin/pm2 save'
```

## Автозапуск при перезагрузке

Цепочка: **systemd → PM2 → gunicorn → Django**

- systemd-сервис: `/etc/systemd/system/pm2-www-root.service`
- PM2 dump: `/var/www/www-root/data/.pm2/dump.pm2` (сохранён через `pm2 save`)

При перезагрузке сервера PM2 автоматически поднимет gunicorn из сохранённого dump.

## Откат (если что-то пойдёт не так)

```bash
# Восстановить оригинальный конфиг
cp /var/www/www-root/data/www/orc-rrmc.ru/ecosystem.config.js.bak /var/www/www-root/data/www/orc-rrmc.ru/ecosystem.config.js

# Перезапустить через PM2
sudo -u www-root bash -c 'export HOME=/var/www/www-root/data && /usr/lib/ispnodejs/lib/node_modules/pm2/bin/pm2 delete orc-rrmc.ru && /usr/lib/ispnodejs/lib/node_modules/pm2/bin/pm2 start /var/www/www-root/data/www/orc-rrmc.ru/ecosystem.config.js && /usr/lib/ispnodejs/lib/node_modules/pm2/bin/pm2 save'
```

## Ключевые файлы

| Файл | Назначение |
|------|------------|
| `/var/www/www-root/data/www/orc-rrmc.ru/ecosystem.config.js` | Конфиг PM2 (gunicorn) |
| `/var/www/www-root/data/www/orc-rrmc.ru/ecosystem.config.js.bak` | Бэкап (runserver) |
| `/var/www/www-root/data/www/orc-rrmc.ru/MedProject/wsgi.py` | WSGI entry point |
| `/var/www/www-root/data/www/orc-rrmc.ru/.venv/bin/gunicorn` | Бинарник gunicorn |
| `/etc/nginx/sites-enabled/orc-rrmc.ru` | Nginx конфиг (proxy → 20000) |
| `/etc/systemd/system/pm2-www-root.service` | Автозапуск PM2 |
| `/var/www/www-root/data/.pm2/dump.pm2` | PM2 saved state |
