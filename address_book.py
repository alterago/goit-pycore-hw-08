"""Address book model: fields, records and the book itself."""

from collections import UserDict
from datetime import date, datetime, timedelta

PHONE_LENGTH = 10
DATE_FORMAT = "%d.%m.%Y"
DAYS_AHEAD = 7  # today and the next six days
SATURDAY = 5
SUNDAY = 6


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Contact name, a required field."""

    def __init__(self, value):
        if not value:
            raise ValueError("Name is required.")
        super().__init__(value)


class Phone(Field):
    """Phone number of exactly 10 digits."""

    def __init__(self, value):
        if not (len(value) == PHONE_LENGTH and value.isdigit()):
            raise ValueError(f"Phone must contain exactly {PHONE_LENGTH} digits.")
        super().__init__(value)


class Birthday(Field):
    """Birthday given as DD.MM.YYYY and stored as a date."""

    def __init__(self, value):
        try:
            birthday = datetime.strptime(value, DATE_FORMAT).date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        if birthday > date.today():
            raise ValueError("Birthday cannot be in the future.")
        super().__init__(birthday)

    def __str__(self):
        return self.value.strftime(DATE_FORMAT)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if self.find_phone(phone):
            raise ValueError(f"Phone {phone} already exists for {self.name.value}.")
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        found = self.find_phone(phone)
        if found is None:
            raise ValueError(f"Phone {phone} not found.")
        self.phones.remove(found)

    def edit_phone(self, old_phone, new_phone):
        found = self.find_phone(old_phone)
        if found is None:
            raise ValueError(f"Phone {old_phone} not found.")
        if new_phone != old_phone and self.find_phone(new_phone):
            raise ValueError(f"Phone {new_phone} already exists for {self.name.value}.")
        # Validate the new number before replacing the old one.
        self.phones[self.phones.index(found)] = Phone(new_phone)

    def find_phone(self, phone):
        for item in self.phones:
            if item.value == phone:
                return item
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones) or "no phones"
        text = f"Contact name: {self.name.value}, phones: {phones}"
        if self.birthday:
            text += f", birthday: {self.birthday}"
        return text


def birthday_in_year(birthday: date, year: int) -> date:
    """Return the birthday in ``year``; 29 February becomes 28 February in a common year."""
    try:
        return birthday.replace(year=year)
    except ValueError:
        return birthday.replace(year=year, day=28)


def move_from_weekend(day: date) -> date:
    """Return the following Monday for a Saturday or a Sunday, otherwise the day itself."""
    if day.weekday() == SATURDAY:
        return day + timedelta(days=2)
    if day.weekday() == SUNDAY:
        return day + timedelta(days=1)
    return day


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        """Return the record by name; the case of the letters does not matter."""
        if name in self.data:
            return self.data[name]
        for stored_name, record in self.data.items():
            if stored_name.lower() == name.lower():
                return record
        return None

    def delete(self, name):
        record = self.find(name)
        if record is not None:
            del self.data[record.name.value]

    def get_upcoming_birthdays(self, today=None):
        """Return who to congratulate within 7 days, today included.

        Each item is a dict with 'name' and 'congratulation_date' (DD.MM.YYYY);
        a birthday on a weekend is congratulated on the following Monday.
        The list is sorted by the congratulation date.
        ``today`` defaults to the current date and exists for testing.
        """
        today = today or date.today()
        upcoming = []
        for record in self.data.values():
            if record.birthday is None:
                continue
            birthday = record.birthday.value
            birthday_this_year = birthday_in_year(birthday, today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_in_year(birthday, today.year + 1)

            if (birthday_this_year - today).days < DAYS_AHEAD:
                upcoming.append((move_from_weekend(birthday_this_year), record.name.value))

        upcoming.sort()
        return [
            {"name": name, "congratulation_date": day.strftime(DATE_FORMAT)}
            for day, name in upcoming
        ]
