import psycopg2
import time
import random
from tabulate import tabulate
from faker import Faker
from datetime import datetime, timedelta

class LibraryDB:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.fake = Faker('uk_UA')
        self.connect()

    def connect(self):
        """Підключення до БД з механізмом повторних спроб"""
        max_retries = 30
        for i in range(max_retries):
            try:
                self.connection = psycopg2.connect(
                    host="postgres",
                    database="library_db",
                    user="admin", 
                    password="password",
                    port="5432"
                )
                self.cursor = self.connection.cursor()
                print("✓ Підключення до бази даних успішне!")
                return
            except Exception as e:
                if i < max_retries - 1:
                    print(f"⌛ Очікування бази даних... ({i+1}/{max_retries})")
                    time.sleep(2)
                else:
                    print(f"✗ Не вдалося підключитися до бази даних: {e}")
                    raise e

    def create_tables(self):
        """Створення таблиць згідно з Варіантом 2"""
        try:
            # Таблиця Книги
            # Додані CHECK constraints для валідації даних на рівні БД
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Books (
                    inventory_number SERIAL PRIMARY KEY,
                    author VARCHAR(100) NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    section VARCHAR(50) CHECK (section IN ('технічна', 'художня', 'економічна')),
                    publication_year INTEGER CHECK (publication_year >= 1900 AND publication_year <= EXTRACT(YEAR FROM CURRENT_DATE)),
                    pages_count INTEGER CHECK (pages_count > 0),
                    price DECIMAL(10,2) CHECK (price >= 0),
                    type VARCHAR(50) CHECK (type IN ('посібник', 'книга', 'періодичне видання')),
                    copies_count INTEGER CHECK (copies_count >= 0),
                    max_loan_days INTEGER CHECK (max_loan_days > 0)
                )
            """)
            
            # Таблиця Читачі
            # Додана перевірка маски телефону (починається з +380 і має 12 цифр)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Readers (
                    reader_ticket_number SERIAL PRIMARY KEY,
                    last_name VARCHAR(50) NOT NULL,
                    first_name VARCHAR(50) NOT NULL,
                    phone VARCHAR(20) CONSTRAINT valid_phone CHECK (phone ~ '^\+380[0-9]{9}$'),
                    address TEXT,
                    course INTEGER CHECK (course BETWEEN 1 AND 4),
                    group_name VARCHAR(20)
                )
            """)
            
            # Таблиця Видачі книжок
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS BookLoans (
                    loan_id SERIAL PRIMARY KEY,
                    loan_date DATE NOT NULL,
                    reader_ticket_number INTEGER REFERENCES Readers(reader_ticket_number) ON DELETE CASCADE,
                    book_inventory_number INTEGER REFERENCES Books(inventory_number) ON DELETE CASCADE
                )
            """)
            
            self.connection.commit()
            print("✓ Таблиці успішно створені або вже існують")
            
        except Exception as e:
            print(f"✗ Помилка при створенні таблиць: {e}")
            self.connection.rollback()

    def clear_data(self):
        """Очищення таблиць перед новою генерацією"""
        try:
            self.cursor.execute("TRUNCATE TABLE BookLoans, Readers, Books RESTART IDENTITY CASCADE;")
            self.connection.commit()
            print("✓ Старі дані очищено")
        except Exception as e:
            self.connection.rollback()
            print(f"Note: Таблиці порожні або ще не створені ({e})")

    def generate_data(self):
        """Заповнення таблиць тестовими даними (Варіант 2)"""
        try:
            # 1. Генерація книг (14 шт)
            sections = ['технічна', 'художня', 'економічна']
            types = ['посібник', 'книга', 'періодичне видання']
            books_data = []
            
            for _ in range(14):
                section = random.choice(sections)
                # Логіка для типу книги залежно від секції (для реалістичності)
                if section == 'художня':
                    book_type = 'книга'
                    max_days = 30
                    title = self.fake.sentence(nb_words=3).rstrip('.')
                else:
                    book_type = random.choice(types)
                    max_days = 14 if book_type == 'періодичне видання' else 21
                    title = self.fake.catch_phrase()

                books_data.append((
                    self.fake.name(), # author
                    title, # title
                    section,
                    random.randint(2000, 2024), # year
                    random.randint(50, 800), # pages
                    round(random.uniform(100, 1500), 2), # price
                    book_type,
                    random.randint(1, 10), # copies
                    max_days
                ))

            self.cursor.executemany("""
                INSERT INTO Books (author, title, section, publication_year, pages_count, price, type, copies_count, max_loan_days)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, books_data)

            # 2. Генерація читачів (9 шт)
            readers_data = []
            for _ in range(9):
                # Генеруємо телефон згідно маски +380XXXXXXXXX
                phone = f"+380{random.randint(50, 99)}{random.randint(1000000, 9999999)}"
                readers_data.append((
                    self.fake.last_name(),
                    self.fake.first_name(),
                    phone,
                    self.fake.city(),
                    random.randint(1, 4), # course
                    f"Группа-{random.randint(100, 200)}"
                ))

            self.cursor.executemany("""
                INSERT INTO Readers (last_name, first_name, phone, address, course, group_name)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, readers_data)

            # 3. Генерація видач (11 шт)
            # Спочатку отримуємо ID створених книг та читачів
            self.cursor.execute("SELECT inventory_number FROM Books")
            book_ids = [row[0] for row in self.cursor.fetchall()]
            
            self.cursor.execute("SELECT reader_ticket_number FROM Readers")
            reader_ids = [row[0] for row in self.cursor.fetchall()]

            loans_data = []
            for _ in range(11):
                loans_data.append((
                    self.fake.date_between(start_date='-2M', end_date='today'),
                    random.choice(reader_ids),
                    random.choice(book_ids)
                ))

            self.cursor.executemany("""
                INSERT INTO BookLoans (loan_date, reader_ticket_number, book_inventory_number)
                VALUES (%s, %s, %s)
            """, loans_data)

            self.connection.commit()
            print("✓ Тестові дані успішно згенеровані (14 книг, 9 читачів, 11 видач)")

        except Exception as e:
            print(f"✗ Помилка при генерації даних: {e}")
            self.connection.rollback()

    def run_queries(self):
        """Виконання запитів згідно завдання (Варіант 2)"""
        print("\n" + "="*80)
        print("ВИКОНАННЯ ЗАПИТІВ (ВАРІАНТ 2)")
        print("="*80)

        queries = [
            {
                "descr": "1. Відобразити всі книги, які були видані після 2001 року. Сортування за назвою.",
                "sql": """
                    SELECT inventory_number, title, author, publication_year 
                    FROM Books 
                    WHERE publication_year > 2001 
                    ORDER BY title
                """
            },
            {
                "descr": "2. Порахувати кількість книг кожного виду (підсумковий запит).",
                "sql": """
                    SELECT type, COUNT(*) as quantity 
                    FROM Books 
                    GROUP BY type
                """
            },
            {
                "descr": "3. Відобразити всіх читачів, які брали посібники. Сортування за прізвищем.",
                "sql": """
                    SELECT DISTINCT r.last_name, r.first_name, r.group_name 
                    FROM Readers r
                    JOIN BookLoans bl ON r.reader_ticket_number = bl.reader_ticket_number
                    JOIN Books b ON bl.book_inventory_number = b.inventory_number
                    WHERE b.type = 'посібник'
                    ORDER BY r.last_name
                """
            },
            {
                "descr": "4. Відобразити всі книги за указаним розділом (параметр: 'технічна').",
                "sql": """
                    SELECT title, author, section, price 
                    FROM Books 
                    WHERE section = 'технічна'
                """
            },
            {
                "descr": "5. Для кожної виданої книги порахувати термін повернення (обчислювальне поле).",
                "sql": """
                    SELECT b.title, bl.loan_date, b.max_loan_days,
                           (bl.loan_date + b.max_loan_days) as return_date
                    FROM BookLoans bl
                    JOIN Books b ON bl.book_inventory_number = b.inventory_number
                """
            },
            {
                "descr": "6. Кількість посібників, книг та періодичних видань в кожному розділі (перехресний).",
                "sql": """
                    SELECT section,
                           COUNT(CASE WHEN type = 'посібник' THEN 1 END) as posibnyky,
                           COUNT(CASE WHEN type = 'книга' THEN 1 END) as knygy,
                           COUNT(CASE WHEN type = 'періодичне видання' THEN 1 END) as periodyka
                    FROM Books
                    GROUP BY section
                """
            }
        ]

        for q in queries:
            print(f"\n🔸 {q['descr']}")
            try:
                self.cursor.execute(q['sql'])
                if self.cursor.description:
                    headers = [desc[0] for desc in self.cursor.description]
                    rows = self.cursor.fetchall()
                    if rows:
                        print(tabulate(rows, headers=headers, tablefmt="psql"))
                    else:
                        print("   [Результатів немає]")
            except Exception as e:
                print(f"   [Помилка виконання]: {e}")
                self.connection.rollback()

    def show_all_tables(self):
        """Виведення всіх таблиць (структура + дані)"""
        print("\n" + "="*80)
        print("ВМІСТ ТАБЛИЦЬ БД")
        print("="*80)
        tables = ['Books', 'Readers', 'BookLoans']
        for table in tables:
            print(f"\n📂 Таблиця: {table}")
            self.cursor.execute(f"SELECT * FROM {table}")
            headers = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()
            print(tabulate(rows, headers=headers, tablefmt="grid"))

    def close(self):
        if self.cursor: self.cursor.close()
        if self.connection: self.connection.close()
        print("\nРоботу завершено.")

if __name__ == "__main__":
    db = LibraryDB()
    db.create_tables()
    db.clear_data() # Очищаємо, щоб не було дублікатів при перезапуску
    db.generate_data()
    db.show_all_tables()
    db.run_queries()
    db.close()