# goit-pycore-hw-08

Homework for topic 12 of the course "Python Programming: Foundations and Best Practices 2.0": the assistant bot from homework 7 now keeps its address book on disk.

The book is saved with `pickle` to `addressbook.pkl` when the bot exits (`close`, `exit`, Ctrl+C or Ctrl+D) and loaded back on the next start.

- `address_book.py` — `Field`, `Name`, `Phone` (10 digits), `Birthday` (DD.MM.YYYY), `Record`, `AddressBook` with `get_upcoming_birthdays`.
- `storage.py` — `save_data` / `load_data`: pickle serialization; a missing file gives an empty book, a damaged one is moved to `addressbook.pkl.corrupted`.
- `main.py` — the console bot; loads the book on start, saves it on any exit; every handler is wrapped in `input_error`.
- `tests.py` — unit tests for validation, birthdays (weekends, year end, 29 February), error messages and saving/loading.

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
