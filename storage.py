"""Saving the address book to disk with pickle and loading it back.

Only load files this program saved itself: unpickling untrusted data can run
arbitrary code.
"""

import os
import pickle
from pathlib import Path

from address_book import AddressBook

# Next to the program, so the book is found whatever folder the bot is started from.
DEFAULT_FILENAME = str(Path(__file__).resolve().with_name("addressbook.pkl"))


class StorageError(Exception):
    """The address book file cannot be read or written."""


def save_data(book, filename=DEFAULT_FILENAME):
    """Save the book with pickle.

    The data is written to a temporary file first and then moved over the old
    one, so an interrupted save never leaves a half-written address book.
    Raises StorageError when the file cannot be written.
    """
    temp_filename = f"{filename}.tmp"
    try:
        with open(temp_filename, "wb") as file:
            pickle.dump(book, file)
        os.replace(temp_filename, filename)
    except OSError as error:
        if os.path.isfile(temp_filename):
            os.remove(temp_filename)
        raise StorageError(f"Cannot save the address book to {filename}: {error.strerror}.") from error


def load_data(filename=DEFAULT_FILENAME):
    """Return the saved book, or a new empty one when there is no file yet.

    A damaged file is renamed to '<filename>.corrupted' so that it is not
    overwritten on exit, and the bot starts with an empty book.
    Raises StorageError when the file exists but cannot be read.
    """
    try:
        with open(filename, "rb") as file:
            book = pickle.load(file)
    except FileNotFoundError:
        return AddressBook()
    except OSError as error:
        raise StorageError(f"Cannot read the address book from {filename}: {error.strerror}.") from error
    except (pickle.UnpicklingError, EOFError, AttributeError, ImportError, IndexError):
        return _set_aside(filename, "is damaged")

    if not isinstance(book, AddressBook):
        return _set_aside(filename, "does not contain an address book")
    return book


def _set_aside(filename, reason):
    """Move an unusable file out of the way and return an empty book."""
    os.replace(filename, f"{filename}.corrupted")
    print(f"{filename} {reason}; it was moved to {filename}.corrupted.")
    return AddressBook()
