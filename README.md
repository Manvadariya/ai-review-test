# Contact Book (Python)

Simple project to practice CRUD operations with clean structure and software-level practices.

## Features
- Add contact
- Search contacts (partial or exact, with optional field filter)
- Update contact
- Delete contact
- Save and load contacts from JSON
- Sort contacts by `name`, `phone`, or `email`
- Bulk add contacts with duplicate strategy: `skip`, `update`, or `error`

## Viva Line
"Implements CRUD operations using dictionaries."

## Project Structure
```
contact_book/
  __init__.py
  models.py
  repository.py
  service.py
  cli.py
main.py
tests/
  test_service.py
```

## Run
```bash
python main.py
```

## Run Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```
