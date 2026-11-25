# Лабораторна робота 8 — ORM та зв’язки

Код виконується у гілці `lab8`, створеній від `lab7`.

## Застосування міграції та демонстраційні дані

У корені репозиторію виконайте:

```powershell
flask --app run.py db upgrade
flask --app run.py seed-lab8
```

Міграція створює `users`, `tags` та асоціативну `post_tags`, додає до `posts` обов’язковий `user_id`, переносить старі рядки автора в користувачів і видаляє текстове поле `author`. Для перенесених профілів використано технічні email-и `example.invalid` і вимкнені паролі (`!`), тому вони не є обліковими записами для входу. Паролі нових користувачів зберігаються у вигляді хешу.

Команда `seed-lab8` ідемпотентна: забезпечує двох користувачів `user1`/`user2`, щонайменше п’ять дописів і теги `Tech`, `Art`, `Science`; демонстраційні дописи мають кілька тегів і авторів із ID 1 та 2.

## Перевірка зв’язків

```powershell
flask --app run.py posts-by-user 2
flask --app run.py posts-by-user 1
flask --app run.py compare-post-loading
flask --app run.py run --port 8080
```

Форма допису завантажує авторів і теги з бази даних. Для вибору кількох тегів утримуйте Ctrl (Windows) або Command (Mac). Сторінка допису показує автора та стилізовані теги; сторінка автора відкривається за посиланням біля імені.

`compare-post-loading` запускає два окремі SQLAlchemy `Session`: звичайне ліниве завантаження і `joinedload(Post.user)` разом із `selectinload(Post.tags)`. Команда друкує дописи та журнал кожного SELECT. У development-конфігурації додатково ввімкнено `SQLALCHEMY_ECHO`.

## Ручне створення користувачів і тегів у Flask shell

```python
from app import db
from app.users.models import User
from app.posts.models import Post, Tag

user1 = User(username="user1", email="user1@example.com", password="")
user1.set_password("change-this-password")
user2 = User(username="user2", email="user2@example.com", password="")
user2.set_password("change-this-password")
db.session.add_all([user1, user2])
db.session.commit()

tag_tech = Tag(name="Tech")
tag_art = Tag(name="Art")
tag_science = Tag(name="Science")
db.session.add_all([tag_tech, tag_art, tag_science])
db.session.commit()
```

Для наявних записів зв’язки можна перевірити та змінити так:

```python
posts_user_2 = db.session.query(Post).filter_by(user_id=2).all()
posts_user_1 = db.session.query(Post).filter_by(user_id=1).all()
post = db.session.get(Post, 1)
post.user_id = 2
post.tags.extend([tag_tech, tag_art])
db.session.commit()
```

Команда `compare-post-loading` є відтворюваною заміною ручного вимірювання для пункту 13: вона виводить фактичну кількість SELECT та SQL-журнал. Запишіть отримані кількості у таблицю звіту:

| Варіант запиту | Кількість дописів | Кількість SELECT |
| --- | ---: | ---: |
| Без `.options()` | 5 | 8 |
| `joinedload()` + `selectinload()` | 5 | 2 |
