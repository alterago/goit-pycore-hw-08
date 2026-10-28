"""Console assistant bot working with an AddressBook.

Commands: hello, add, change, phone, all, add-birthday, show-birthday,
birthdays, close / exit. Ctrl+C or Ctrl+D also exits.

The address book is loaded from addressbook.pkl (next to this file) on start
and saved back on exit.
"""

from datetime import datetime
from functools import wraps

from address_book import DATE_FORMAT, AddressBook, Record
from storage import StorageError, load_data, save_data


def input_error(func):
    """Turn errors raised by a handler into messages for the user."""

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as error:
            return str(error)
        except KeyError as error:
            return f"Contact {error} not found."
        except IndexError:
            return "Enter the argument for the command."

    return inner


def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return ("",)
    cmd, *args = parts
    return cmd.strip().lower(), *args


def require_args(args, count, usage):
    """Raise ValueError with a usage hint when there are too few arguments."""
    if len(args) < count:
        raise ValueError(f"Usage: {usage}")


def get_record(book, name):
    """Return the record or raise KeyError when there is no such contact."""
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    return record


@input_error
def add_contact(args, book: AddressBook):
    require_args(args, 2, "add <name> <phone>")
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        message = "Contact added."
    if phone:
        record.add_phone(phone)  # an invalid phone raises before a new record is stored
    book.add_record(record)
    return message


@input_error
def change_contact(args, book: AddressBook):
    require_args(args, 3, "change <name> <old phone> <new phone>")
    name, old_phone, new_phone, *_ = args
    get_record(book, name).edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    require_args(args, 1, "phone <name>")
    record = get_record(book, args[0])
    if not record.phones:
        return f"{record.name.value} has no phones."
    return f"{record.name.value}: {'; '.join(p.value for p in record.phones)}"


@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "No contacts saved."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book: AddressBook):
    require_args(args, 2, "add-birthday <name> <DD.MM.YYYY>")
    name, birthday, *_ = args
    get_record(book, name).add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book: AddressBook):
    require_args(args, 1, "show-birthday <name>")
    record = get_record(book, args[0])
    if record.birthday is None:
        return f"{record.name.value} has no birthday set."
    return f"{record.name.value}: {record.birthday}"


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    # Group the names by congratulation day; the list is already sorted by date.
    by_day = {}
    for item in upcoming:
        by_day.setdefault(item["congratulation_date"], []).append(item["name"])
    lines = []
    for day, names in by_day.items():
        weekday = datetime.strptime(day, DATE_FORMAT).strftime("%A")
        lines.append(f"{weekday} {day}: {', '.join(names)}")
    return "\n".join(lines)


def main():
    try:
        book = load_data()
    except StorageError as error:
        print(error)
        print("The bot was not started, so the saved contacts are not overwritten.")
        return

    print("Welcome to the assistant bot!")
    if book.data:
        print(f"Loaded {len(book.data)} contact(s) from the previous session.")
    try:
        run_bot(book)
    finally:
        # Runs on close/exit, Ctrl+C, Ctrl+D and on an unexpected error.
        try:
            save_data(book)
        except StorageError as error:
            print(error)


def run_bot(book: AddressBook):
    while True:
        try:
            user_input = input("Enter a command: ")
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C or Ctrl+D ends the bot the same way as "exit".
            print("\nGood bye!")
            break
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
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
            print(show_all(book))
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
