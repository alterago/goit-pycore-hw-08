"""Tests for the address book, storage and the bot handlers: python -m unittest tests.py"""

import os
import tempfile
import unittest
from datetime import date

from address_book import AddressBook, Birthday, Phone, Record
from main import add_birthday, add_contact, birthdays, change_contact, show_birthday, show_phone
from storage import load_data, save_data


def book_with_birthdays(items):
    book = AddressBook()
    for name, birthday in items:
        record = Record(name)
        record.add_birthday(birthday)
        book.add_record(record)
    return book


class FieldsTest(unittest.TestCase):
    def test_phone_needs_exactly_ten_digits(self):
        self.assertEqual(Phone("1234567890").value, "1234567890")
        for bad in ["123", "12345678901", "12345abcde", ""]:
            with self.assertRaises(ValueError):
                Phone(bad)

    def test_birthday_format_and_future(self):
        self.assertEqual(str(Birthday("30.10.1990")), "30.10.1990")
        for bad in ["1990-10-30", "31.02.1990", "30/10/1990", ""]:
            with self.assertRaises(ValueError):
                Birthday(bad)
        with self.assertRaises(ValueError):
            Birthday("01.01.2999")


class RecordTest(unittest.TestCase):
    def test_duplicate_phone_is_rejected(self):
        record = Record("John")
        record.add_phone("1234567890")
        with self.assertRaises(ValueError):
            record.add_phone("1234567890")
        self.assertEqual(len(record.phones), 1)

    def test_edit_keeps_old_phone_when_new_is_invalid(self):
        record = Record("John")
        record.add_phone("1234567890")
        with self.assertRaises(ValueError):
            record.edit_phone("1234567890", "12")
        self.assertEqual(record.phones[0].value, "1234567890")


class AddressBookTest(unittest.TestCase):
    def test_find_ignores_case(self):
        book = AddressBook()
        book.add_record(Record("John"))
        self.assertIs(book.find("john"), book.find("John"))
        self.assertIsNone(book.find("Bob"))

    def test_upcoming_birthdays_window_and_weekends(self):
        # Wednesday 28.10.2026: the window is 28.10 .. 03.11.
        book = book_with_birthdays([
            ("Today", "28.10.1990"),
            ("Saturday", "31.10.1990"),
            ("Sunday", "01.11.1990"),
            ("LastDay", "03.11.1990"),
            ("TooLate", "04.11.1990"),
            ("Yesterday", "27.10.1990"),
        ])
        self.assertEqual(book.get_upcoming_birthdays(today=date(2026, 10, 28)), [
            {"name": "Today", "congratulation_date": "28.10.2026"},
            {"name": "Saturday", "congratulation_date": "02.11.2026"},
            {"name": "Sunday", "congratulation_date": "02.11.2026"},
            {"name": "LastDay", "congratulation_date": "03.11.2026"},
        ])

    def test_upcoming_birthdays_year_end_and_leap_day(self):
        book = book_with_birthdays([("NewYear", "02.01.1990")])
        self.assertEqual(book.get_upcoming_birthdays(today=date(2026, 12, 28)),
                         [{"name": "NewYear", "congratulation_date": "04.01.2027"}])
        book = book_with_birthdays([("Leap", "29.02.2000")])
        self.assertEqual(book.get_upcoming_birthdays(today=date(2027, 2, 25)),
                         [{"name": "Leap", "congratulation_date": "01.03.2027"}])


class HandlersTest(unittest.TestCase):
    def test_add_with_invalid_phone_creates_nothing(self):
        book = AddressBook()
        self.assertEqual(add_contact(["Jane", "12345"], book), "Phone must contain exactly 10 digits.")
        self.assertEqual(len(book), 0)
        self.assertEqual(add_contact(["Jane", "9876543210"], book), "Contact added.")
        self.assertEqual(add_contact(["jane", "1112223333"], book), "Contact updated.")
        self.assertEqual(show_phone(["Jane"], book), "Jane: 9876543210; 1112223333")

    def test_error_messages_are_specific(self):
        book = AddressBook()
        self.assertEqual(add_contact([], book), "Usage: add <name> <phone>")
        self.assertEqual(change_contact(["Bob", "1", "2"], book), "Contact 'Bob' not found.")
        self.assertEqual(add_birthday(["Bob"], book), "Usage: add-birthday <name> <DD.MM.YYYY>")
        add_contact(["Ann", "1231231234"], book)
        self.assertEqual(show_birthday(["Ann"], book), "Ann has no birthday set.")
        self.assertEqual(add_birthday(["Ann", "1990-10-30"], book), "Invalid date format. Use DD.MM.YYYY")

    def test_birthdays_command_groups_by_day(self):
        today = date.today()
        if (today.month, today.day) == (2, 29):
            self.skipTest("29 February moves to 28 February in common years")
        book = AddressBook()
        for name in ["Ann", "Bob"]:
            add_contact([name, "1231231234"], book)
            add_birthday([name, today.replace(year=1990).strftime("%d.%m.%Y")], book)
        line = birthdays([], book)
        self.assertEqual(line.count("\n"), 0)  # both on the same day
        self.assertTrue(line.endswith(": Ann, Bob"))


class StorageTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.filename = os.path.join(self.folder.name, "addressbook.pkl")

    def tearDown(self):
        self.folder.cleanup()

    def test_book_survives_save_and_load(self):
        book = AddressBook()
        add_contact(["John", "1234567890"], book)
        add_birthday(["John", "30.10.1990"], book)
        save_data(book, self.filename)

        restored = load_data(self.filename)
        self.assertIsInstance(restored, AddressBook)
        self.assertEqual(str(restored.find("John")), str(book.find("John")))
        self.assertEqual(show_birthday(["John"], restored), "John: 30.10.1990")

    def test_missing_file_gives_empty_book(self):
        book = load_data(self.filename)
        self.assertIsInstance(book, AddressBook)
        self.assertEqual(len(book), 0)

    def test_damaged_file_is_kept_aside(self):
        with open(self.filename, "wb") as file:
            file.write(b"not a pickle")
        book = load_data(self.filename)
        self.assertEqual(len(book), 0)
        self.assertTrue(os.path.exists(f"{self.filename}.corrupted"))
        self.assertFalse(os.path.exists(self.filename))


if __name__ == "__main__":
    unittest.main()
