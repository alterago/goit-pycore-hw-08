"""Saving the address book to disk with pickle and loading it back."""

import os
import pickle

from address_book import AddressBook

DEFAULT_FILENAME = "addressbook.pkl"


def save_data(book, filename=DEFAULT_FILENAME):
    """Save the book with pickle.

    The data is written to a temporary file first and then moved over the old
    one, so an interrupted save never leaves a half-written address book.
    """
    temp_filename = f"{filename}.tmp"
    with open(temp_filename, "wb") as file:
        pickle.dump(book, file)
    os.replace(temp_filename, filename)


def load_data(filename=DEFAULT_FILENAME):
    """Return the saved book, or a new empty one when there is no file yet.

    A damaged file is renamed to '<filename>.corrupted' so that it is not
    overwritten on exit, and the bot starts with an empty book.
    """
    try:
        with open(filename, "rb") as file:
            book = pickle.load(file)
    except FileNotFoundError:
        return AddressBook()
    except (pickle.UnpicklingError, EOFError, AttributeError, ImportError, IndexError):
        os.replace(filename, f"{filename}.corrupted")
        print(f"Saved data in {filename} is damaged; it was moved to {filename}.corrupted.")
        return AddressBook()

    if not isinstance(book, AddressBook):
        os.replace(filename, f"{filename}.corrupted")
        print(f"{filename} does not contain an address book; it was moved to {filename}.corrupted.")
        return AddressBook()
    return book
