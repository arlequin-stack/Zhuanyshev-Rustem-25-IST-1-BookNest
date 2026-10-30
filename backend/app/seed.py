from sqlalchemy import select
from app.database import SessionLocal
from app.models import Author, Book, Genre, Profile, User
from app.security import hash_password

BOOKS = [
    ("Мастер и Маргарита", "Михаил Булгаков", "9785170902508", 1967, 4.9, "Роман о свободе, любви и цене выбора в городе, где реальность постоянно спорит с фантазией."),
    ("Чистый код", "Роберт Мартин", "9785446109655", 2008, 4.7, "Практическое руководство по созданию читаемого, поддерживаемого и профессионального программного обеспечения."),
    ("Цветы для Элджернона", "Дэниел Киз", "9785041067732", 1966, 4.8, "История интеллектуального эксперимента, человечности и ответственности за научные решения."),
    ("Проектирование API", "Арно Лорет", "9781617295102", 2019, 4.5, "Системный подход к проектированию понятных и устойчивых программных интерфейсов."),
    ("Атомные привычки", "Джеймс Клир", "9785041166854", 2018, 4.6, "Метод небольших изменений, которые постепенно формируют устойчивые привычки и результат."),
    ("Краткая история времени", "Стивен Хокинг", "9785171005451", 1988, 4.7, "Доступный разговор о происхождении Вселенной, времени, гравитации и чёрных дырах."),
]

def seed() -> None:
    with SessionLocal() as db:
        librarian = db.scalar(select(User).where(User.email == "librarian@example.com"))
        if not librarian:
            librarian = User(
                email="librarian@example.com",
                password_hash=hash_password("Library123"),
                role="librarian",
                profile=Profile(full_name="Демо-библиотекарь"),
            )
            db.add(librarian)
        if db.scalar(select(Book.id).limit(1)):
            db.commit()
            return
        fiction = Genre(name="Художественная литература")
        technology = Genre(name="Технологии")
        nonfiction = Genre(name="Нон-фикшн")
        db.add_all([fiction, technology, nonfiction])
        authors: dict[str, Author] = {}
        for index, (title, author_name, isbn, year, rating, description) in enumerate(BOOKS):
            author = authors.setdefault(author_name, Author(name=author_name))
            genre = technology if index in (1, 3) else nonfiction if index in (4, 5) else fiction
            db.add(Book(title=title, author=author, isbn=isbn, year=year, rating=rating, description=description, copies_total=3, copies_available=3, genres=[genre]))
        db.commit()

if __name__ == "__main__":
    seed()
