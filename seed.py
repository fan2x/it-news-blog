from datetime import datetime

from app import Author, Comment, Post, Profile, Tag, app, db

with app.app_context():
    db.drop_all()
    db.create_all()

    alexey = Author(username="alexey")
    alexey.set_password("123456")
    alexey.profile = Profile(full_name="Алексей Смирнов", about="Backend-разработчик, пишу на Python.")

    anna = Author(username="anna")
    anna.set_password("123456")
    anna.profile = Profile(full_name="Анна Соколова", about="Интересуюсь информационной безопасностью.")

    python = Tag(name="python")
    security = Tag(name="безопасность")
    web = Tag(name="веб")

    post1 = Post(
        title="Вышел Python 3.13",
        text="В новой версии появилась экспериментальная сборка без GIL и первый JIT-компилятор.\n"
        "Также обновили интерактивную консоль: теперь в ней есть подсветка и многострочное редактирование.",
        created_at=datetime(2026, 9, 20, 10, 30),
        author=alexey,
        tags=[python],
    )
    post2 = Post(
        title="Почему пароли хранят в виде хеша",
        text="Если база утечёт, пароли в открытом виде сразу попадут к злоумышленнику.\n"
        "Поэтому сервер хранит хеш пароля, а к паролю перед хешированием добавляет случайную соль.",
        created_at=datetime(2026, 9, 24, 15, 0),
        author=anna,
        tags=[security, web],
    )
    post3 = Post(
        title="Flask — простой веб-фреймворк на Python",
        text="Flask умеет маршрутизацию и шаблоны Jinja2, а остальное подключается расширениями.\n"
        "Например, Flask-SQLAlchemy для базы данных и Flask-Login для входа пользователей.",
        created_at=datetime(2026, 9, 28, 18, 45),
        author=alexey,
        tags=[python, web],
    )

    comments = [
        Comment(text="Жду, когда библиотеки начнут поддерживать сборку без GIL.", author=anna, post=post1),
        Comment(text="Полезно, спасибо за объяснение про соль!", author=alexey, post=post2),
        Comment(text="Для учебных проектов Flask — отличный выбор.", author=anna, post=post3),
    ]

    db.session.add_all([alexey, anna, post1, post2, post3, *comments])
    db.session.commit()
    print("Демо-данные добавлены. Вход: alexey или anna, пароль 123456")
