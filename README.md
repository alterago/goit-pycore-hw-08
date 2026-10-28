# goit-pycore-hw-08

Homework for topic 12 of the course "Python Programming: Foundations and Best Practices 2.0": the assistant bot from homework 7 now keeps its address book on disk.

The book is saved with `pickle` to `addressbook.pkl` when the bot exits (`close`, `exit`, Ctrl+C or Ctrl+D) and loaded back on the next start. The file lives next to `main.py`, so the same book is found whatever folder the bot is started from.

File problems are reported with a clear message instead of a traceback:

- no file yet — the bot starts with an empty book;
- a damaged file (empty, not a pickle, not an address book) — it is moved to `addressbook.pkl.corrupted` and the bot starts with an empty book;
- the file cannot be read (permissions, a folder in its place) — the bot does not start, so the saved contacts are not overwritten;
- the book cannot be saved (read-only folder) — the reason is printed; the old file stays intact because saving goes through a temporary file.

Only load a file this program saved itself: unpickling untrusted data can run arbitrary code.

- `address_book.py` — `Field`, `Name`, `Phone` (10 digits), `Birthday` (DD.MM.YYYY), `Record`, `AddressBook` with `get_upcoming_birthdays`.
- `storage.py` — `save_data` / `load_data`: pickle serialization; a missing file gives an empty book, a damaged one is moved to `addressbook.pkl.corrupted`.
- `main.py` — the console bot; loads the book on start, saves it on any exit; every handler is wrapped in `input_error`.
- `tests.py` — unit tests for validation, birthdays (weekends, year end, 29 February), error messages and saving/loading, including damaged and unreadable files.

## Run

```bash
python main.py
python -m unittest tests.py
```

## Commands

| Command | Action |
|---|---|
| `add <name> <phone>` | add a contact or a phone to an existing contact |
| `change <name> <old phone> <new phone>` | change a phone |
| `phone <name>` | show the contact's phones |
| `all` | show all contacts |
| `add-birthday <name> <DD.MM.YYYY>` | add a birthday |
| `show-birthday <name>` | show the birthday |
| `birthdays` | who to congratulate in the next 7 days, grouped by day (weekend birthdays move to Monday) |
| `hello` | greeting |
| `close` / `exit` | quit (Ctrl+C or Ctrl+D also quits) |

Names are matched regardless of case; a phone cannot be added to the same contact twice.
