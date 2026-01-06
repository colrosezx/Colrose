# Руководство по развертыванию проекта Colrose

Этот документ описывает, как настраивать, развертывать и обслуживать проект Colrose с использованием Docker. Мы внедрили современный подход к управлению секретами (паролями, ключами) через Docker Secrets, чтобы избежать хранения чувствительных данных в файлах на продакшен-сервере.

## 1. Концепция Управления Секретами

Вместо того чтобы хранить `.env` файлы на сервере, мы используем **Docker Secrets**.

- **На продакшене:** Секреты (данные из `.env` и SSL-сертификаты) один раз загружаются в зашифрованное хранилище Docker на сервере. Самих файлов `.env` или `.crt`/`.key` на диске сервера **не остается**. Контейнеры получают доступ к этим секретам через виртуальные файлы в директории `/run/secrets/`.
- **Локально:** Для удобства разработки `docker-compose` использует локальный файл `.env` для конфигурации. Этот файл не должен попадать в Git (убедитесь, что он в `.gitignore`). 

---

## 2. Локальная разработка

Эти шаги предназначены для запуска проекта на вашем компьютере.

### Шаг 2.1: Подготовка

1.  **Установите Docker и Docker Compose.**
2.  **Создайте файл `.env`:** Скопируйте `.env-example` в `.env` и заполните его вашими **локальными** данными для разработки.

    ```sh
    cp .env.example .env
    ```
    *   Укажите `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.
    *   Установите `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1`.
    *   Убедитесь, что файл сохранен в формате **LF (Unix)**, а не CRLF (Windows).

### Шаг 2.2: Первый запуск

1.  **Запустите все сервисы:**

    ```sh
    docker-compose -f docker-compose.yml up -d --build
    ```
    При первом запуске эта команда создаст Docker-тома (volumes) для базы данных, статики и медиафайлов.

2.  **Выполните миграции базы данных:**

    ```sh
    docker-compose -f docker-compose.yml exec backend python manage.py migrate
    ```

3.  **(Опционально) Загрузите статьи:** Чтобы наполнить базу данных контентом, выполните:
    ```sh
    docker-compose -f docker-compose.yml exec backend python manage.py import_posts
    ```

### Шаг 2.3: Доступ к приложению

-   **HTTP:** `http://localhost`
-   **HTTPS:** `https://localhost:8443` (вам нужно будет принять предупреждение безопасности в браузере, так как используется самоподписанный SSL-сертификат).

---

## 3. Развертывание на Продакшене

Эти шаги предназначены для развертывания на "боевом" сервере.

### Шаг 3.1: Подготовка сервера

1.  **Клонируйте репозиторий** на ваш сервер.
2.  **Активируйте Docker Swarm Mode:** Это необходимо для работы Docker Secrets. Если у вас один сервер, команда очень простая:
    ```sh
    docker swarm init
    ```
    (Если Swarm уже активен, вы увидите сообщение об этом — это нормально).

### Шаг 3.2: Загрузка секретов

**Это самый важный шаг.** Эти команды нужно выполнить на сервере **один раз**. Они загружают содержимое ваших файлов в безопасное хранилище Docker. Сами файлы после этого на сервере не нужны.

1.  **Секрет с переменными окружения:**
    Создайте на сервере временный файл `production.env` с вашими **реальными** данными для продакшена (`SECRET_KEY`, `POSTGRES_PASSWORD`, `DJANGO_ALLOWED_HOSTS=colrose.ru,www.colrose.ru` и т.д.). Затем выполните:
    ```sh
    docker secret create backend_env production.env
    # После этого файл production.env можно и нужно удалить!
    rm production.env
    ```

2.  **Секреты для SSL-сертификатов:**
    Скопируйте ваши SSL-сертификаты на сервер, создайте из них секреты, а затем удалите файлы сертификатов.
    ```sh
    # Замените /path/to/ на ваш путь
    docker secret create ssl_cert /path/to/your/fullchain.pem
    docker secret create ssl_key /path/to/your/privkey.pem
    # После этого файлы сертификатов можно и нужно удалить!
    ```

### Шаг 3.3: Запуск приложения

1.  **Запустите стек:**
    ```sh
    docker-compose -f docker-compose.prod.yml up -d --build
    ```
2.  **Выполните миграции:**
    ```sh
    docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
    ```
3.  **(Опционально) Загрузите статьи:**
    ```sh
    docker-compose -f docker-compose.prod.yml exec backend python manage.py import_posts
    ```

Ваше приложение будет доступно по вашему домену.

---

## 4. Резервное копирование (Бэкапы)

Бэкапы создаются путем запуска временного контейнера, который архивирует данные из Docker-томов. Готовые архивы сохраняются в папку `backups/`.

### 4.1. Бэкап Медиафайлов (Загруженный контент)

Эта команда создает архив тома `colrose_media_volume`.

```sh
docker run --rm --mount source=colrose_media_volume,target=/media,readonly -v "$(pwd)/backups":/backup_output alpine \
  tar -czf /backup_output/media_backup_$(date +%Y-%m-%d_%H-%M-%S).tar.gz -C /media .
```

### 4.2. Бэкап Статических файлов (CSS, JS)

Эта команда создает архив тома `colrose_static_volume`. Обычно бэкап этих файлов менее критичен, так как их можно пересобрать командой `collectstatic`, но он может быть полезен.

```sh
docker run --rm --mount source=colrose_static_volume,target=/static,readonly -v "$(pwd)/backups":/backup_output alpine \
  tar -czf /backup_output/static_backup_$(date +%Y-%m-%d_%H-%M-%S).tar.gz -C /static .
```

### 4.3. Бэкап Базы Данных

Эта команда выполняет `pg_dump` внутри контейнера `db` и сохраняет результат в папку `backups/`. **Не забудьте подставить актуальные `POSTGRES_USER` и `POSTGRES_DB`** из вашего `.env` файла.

```sh
# Замените POSTGRES_USER и POSTGRES_DB на реальные значения
docker-compose exec -T db pg_dump -U POSTGRES_USER POSTGRES_DB > backups/db_backup_$(date +%Y-%m-%d_%H-%M-%S).sql
```

### 4.4. Автоматизация на Продакшене

На продакшен-сервере эти команды следует добавить в `cron` для регулярного выполнения. 