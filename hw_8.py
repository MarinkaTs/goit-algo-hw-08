import pickle
from collections import UserDict
from datetime import datetime, timedelta

# Класи та функції  
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number should contain 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime('%d.%m.%Y')

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if str(phone) == old_phone:
                phone.value = new_phone
                break

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return str(p)
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = '; '.join(map(str, self.phones))
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for name, record in self.data.items():
            if record.birthday:
                birthday = datetime.strptime(str(record.birthday), "%d.%m.%Y").date().replace(year=today.year)
                
                # Перевірка, чи день народження вже минув у цьому році
                if birthday < today:
                    # Якщо так, розглядаємо дату на наступний рік
                    birthday = birthday.replace(year=today.year + 1)
                
                # Визначення різниці між днем народження та поточним днем
                days_until_birthday = (birthday - today).days
                
                # Перевірка, чи день народження припадає на вихідний
                if (today + timedelta(days_until_birthday)).weekday() in [5, 6]:  # 5 та 6 - субота та неділя
                    # Якщо так, перенесення дати привітання на наступний понеділок
                    days_until_birthday += (7 - (today + timedelta(days_until_birthday)).weekday())
                
                # Додавання інформації про користувача та дату привітання до результату
                congratulation_date = today + timedelta(days_until_birthday)
                upcoming_birthdays.append({"name": name, "congratulation_date": congratulation_date.strftime("%Y.%m.%d")})
        
        return upcoming_birthdays
    
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

# Декоратори та функції 
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name, phone, or birthday please."
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid command format."

    return inner

@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise ValueError
    name, phone = args
    record = Record(name.lower())
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."

@input_error
def change_contact(args, book):
    if len(args) < 2:
        raise ValueError
    name, new_phone = args
    record = book.find(name.lower())
    if not record:
        raise KeyError
    record.edit_phone(record.phones[0].value, new_phone)
    return "Contact updated."

@input_error
def show_phone(args, book):
    if len(args) < 1:
        raise ValueError
    name, = args
    record = book.find(name.lower())
    return record.phones[0].value if record else "Contact not found."

@input_error
def add_birthday(args, book):
    if len(args) < 2:
        raise ValueError
    name, birthday = args
    record = book.find(name.lower())
    if not record:
        raise KeyError
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    if len(args) < 1:
        raise ValueError
    name, = args
    record = book.find(name.lower())
    return record.birthday.value if record and record.birthday else "Contact not found."

def get_upcoming_birthdays(book):
    today = datetime.today().date()
    upcoming_birthdays = []

    for name, record in book.data.items():
        if record.birthday:
            birthday = datetime.strptime(str(record.birthday.value), "%d.%m.%Y").date().replace(year=today.year)
            
            if birthday < today:
                birthday = birthday.replace(year=today.year + 1)
            
            days_until_birthday = (birthday - today).days
            
            if (today + timedelta(days_until_birthday)).weekday() in [5, 6]:
                days_until_birthday += (7 - (today + timedelta(days_until_birthday)).weekday())
            
            congratulation_date = today + timedelta(days_until_birthday)
            upcoming_birthdays.append({"name": name, "congratulation_date": congratulation_date.strftime("%Y.%m.%d")})
    
    return upcoming_birthdays

@input_error
def birthdays(args, book):
    upcoming_birthdays = get_upcoming_birthdays(book)
    return f"Upcoming birthdays: {upcoming_birthdays}"

def main():
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").lower()
        command, *args = user_input.split()

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)  # Збереження даних при виході з програми
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            for name, record in book.data.items():
                print(record)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()