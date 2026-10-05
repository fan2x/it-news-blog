# IT-Новости — мини-блог на Flask

Учебный проект для пересдачи.
**Автор:** Мельников Семен Александрович

Пользователи регистрируются, публикуют статьи (заголовок, текст, дата, теги), читают общую ленту и оставляют комментарии под статьями. У каждого автора есть страница с профилем и списком статей.

## Что используется

- **Flask** — маршруты (`@app.route`).
- **Jinja2** — шаблоны: `{{ }}`, `{% %}`, `{# #}`; все страницы наследуются от `base.html` через `extends` и `block`, в заголовке страниц используется `super()`.
- **Flask-SQLAlchemy** — модели `Author`, `Profile`, `Post`, `Comment`, `Tag` и все три вида связей:
  - один-ко-многим: автор → статьи, автор → комментарии, статья → комментарии;
  - многие-ко-многим: статьи ↔ теги (таблица `post_tags`);
  - один-к-одному: автор ↔ профиль (`uselist=False`).
- **Flask-Login** — `login_user`, `logout_user`, `current_user`, `@login_required`.
- **Пароли** хранятся как хеш с солью: `generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)`.
- **Формы** обрабатываются через `request.form`, **поиск и фильтр по тегу** — через `request.args` (например, `/?q=flask` или `/?tag=python`).

## Структура

```
app.py          — приложение: модели и все маршруты
seed.py         — демо-данные
start.command   — запуск двойным щелчком (macOS)
templates/      — шаблоны Jinja2
static/         — стили
```

## Запуск

На macOS — двойной щелчок по `start.command`.

Вручную:

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                  # демо-данные (необязательно)
python app.py
```

Сайт откроется по адресу http://127.0.0.1:5001

Демо-вход: `alexey` или `anna`, пароль `123456`.
