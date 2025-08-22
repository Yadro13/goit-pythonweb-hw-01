from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional, List
from datetime import datetime

MIN_YEAR = 1450
CURRENT_YEAR = datetime.now().year

# SRP: окремий клас-контейнер для сутності "Книга"
@dataclass(frozen=True)
class Book:
    title: str
    author: str
    year: int

    def __str__(self) -> str:
        return f'Title: {self.title}, Author: {self.author}, Year: {self.year}'


# ISP: вузький інтерфейс бібліотеки — лише те, що справді потрібно менеджеру
class LibraryInterface(ABC):
    @abstractmethod
    def add_book(self, book: Book) -> None: ...
    @abstractmethod
    def remove_book(self, title: str) -> bool: ...
    @abstractmethod
    def get_all(self) -> Iterable[Book]: ...
    @abstractmethod
    def find_by_title(self, title: str) -> Optional[Book]: ...


# Базова реалізація: in-memory сховище
# Відповідає LSP: будь-яка інша реалізація з таким же інтерфейсом повинна працювати так само
class Library(LibraryInterface):
    def __init__(self) -> None:
        self._books: List[Book] = []

    def add_book(self, book: Book) -> None:
        self._books.append(book)

    def remove_book(self, title: str) -> bool:
        for i, b in enumerate(self._books):
            if b.title == title:
                del self._books[i]
                return True
        return False

    def get_all(self) -> Iterable[Book]:
        # Повертаємо копію, щоб зовнішній код не ламав інваріанти колекції
        return list(self._books)

    def find_by_title(self, title: str) -> Optional[Book]:
        for b in self._books:
            if b.title == title:
                return b
        return None


# OCP-приклад: розширення без зміни Library — декоратор із логуванням
class LoggedLibrary(LibraryInterface):
    def __init__(self, inner: LibraryInterface) -> None:
        self._inner = inner

    def add_book(self, book: Book) -> None:
        print(f"[LOG] add: {book.title}")
        self._inner.add_book(book)

    def remove_book(self, title: str) -> bool:
        print(f"[LOG] remove: {title}")
        return self._inner.remove_book(title)

    def get_all(self) -> Iterable[Book]:
        print("[LOG] get_all")
        return self._inner.get_all()

    def find_by_title(self, title: str) -> Optional[Book]:
        print(f"[LOG] find: {title}")
        return self._inner.find_by_title(title)


# DIP: менеджер залежить від абстракції LibraryInterface, а не конкретного класу
class LibraryManager:
    def __init__(self, library: LibraryInterface) -> None:
        self.library = library

    # ---- helpers (інкапсулюємо валідацію тут, а не в моделях/репо) ----
    def _normalize(self, s: str) -> str:
        return " ".join(s.split())

    def _validate_title(self, title: str) -> bool:
        if not title or not title.strip():
            print("Title cannot be empty.")
            return False
        if len(title.strip()) < 2:
            print("Title is too short (min 2 chars).")
            return False
        if len(title) > 255:
            print("Title is too long (max 255 chars).")
            return False
        return True

    def _validate_author(self, author: str) -> bool:
        if not author or not author.strip():
            print("Author cannot be empty.")
            return False
        a = author.strip()
        if len(a) < 2:
            print("Author is too short (min 2 chars).")
            return False
        if len(a) > 255:
            print("Author is too long (max 255 chars).")
            return False
        # Проста перевірка, щоб не було суцільних цифр/сміття
        if a.isdigit():
            print("Author cannot be only digits.")
            return False
        return True

    def _validate_year(self, year_str: str) -> tuple[bool, int | None]:
        try:
            y = int(year_str)
        except ValueError:
            print("Year must be an integer.")
            return False, None
        if y < 0:
            print("Year cannot be negative.")
            return False, None
        if y < MIN_YEAR:
            print(f"Year is too early (min {MIN_YEAR}).")
            return False, None
        if y > CURRENT_YEAR:
            print(f"Year cannot be in the future (max {CURRENT_YEAR}).")
            return False, None
        return True, y

    def _exists(self, title: str, author: str, books: Iterable[Book]) -> bool:
        t = title.lower()
        a = author.lower()
        return any(b.title.lower() == t and b.author.lower() == a for b in books)

    # ---- публічні методи для CLI ----
    def add_book(self, title: str, author: str, year: str) -> None:
        title = self._normalize(title)
        author = self._normalize(author)

        if not (self._validate_title(title) and self._validate_author(author)):
            return

        ok, y = self._validate_year(year)
        if not ok:
            return

        # унікальність: title+author
        all_books = list(self.library.get_all())
        if self._exists(title, author, all_books):
            print("Such a book already exists (same title and author).")
            return

        self.library.add_book(Book(title=title, author=author, year=y))
        print("Book added.")

    def remove_book(self, title: str) -> None:
        title = self._normalize(title)
        ok = self.library.remove_book(title)
        print("Book removed." if ok else "Book not found.")

    def show_books(self) -> None:
        books = list(self.library.get_all())
        if not books:
            print("No books in library.")
            return
        for b in books:
            print(str(b))


def main() -> None:
    # Можемо легко поміняти реалізацію, не чіпаючи manager:
    # lib = Library()
    lib = LoggedLibrary(Library())

    manager = LibraryManager(lib)

    while True:
        command = input("Enter command (add, remove, show, exit): ").strip().lower()
        match command:
            case "add":
                title = input("Enter book title: ").strip()
                author = input("Enter book author: ").strip()
                year = input("Enter book year: ").strip()
                manager.add_book(title, author, year)
            case "remove":
                title = input("Enter book title to remove: ").strip()
                manager.remove_book(title)
            case "show":
                manager.show_books()
            case "exit":
                break
            case _:
                print("Invalid command. Please try again.")


if __name__ == "__main__":
    main()
