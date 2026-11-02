# Document Management Backend — Earlier Version

A Django backend for a document-management application. The repository contains a Django project, an application module, a PDF directory and a local SQLite database.

## Local setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Repository hygiene

This repository currently includes a local SQLite database and a PDF directory. It is kept private until the database and uploaded files have been reviewed and replaced with synthetic examples. Do not commit user documents, access tokens or secrets.

For the newer frontend/backend split, see [ManageMyDocument](https://github.com/Sandeep-kumar-IITR/ManageMyDocument) and [ManageMyDoc](https://github.com/Sandeep-kumar-IITR/ManageMyDoc).

## Author

Sandeep Kumar
