# Antidrone - B2B Tech Catalog

Django-based B2B technology catalog with hierarchical categories.

## Features

- Hierarchical product categories (django-mptt)
- Product management with multiple images
- Admin panel for content management
- Bootstrap 5 responsive UI
- SEO-friendly URLs with slugs

## Requirements

- Python 3.10+
- Django 4.2+

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd antidrone-project
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from example:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Usage

- Admin panel: http://127.0.0.1:8000/admin/
- Catalog: http://127.0.0.1:8000/catalog/

## Test Data

Load test data (categories and products) for development:

```bash
python manage.py load_test_data
```

Clear all catalog data:

```bash
python manage.py load_test_data --clear
```

This creates:
- 2 main categories: Антени, Модулі
- 8 subcategories (4 per main category)
- 18 products with realistic specs and prices

## Project Structure

```
antidrone-project/
├── antidrone/          # Django project configuration
├── catalog/            # Catalog application
├── templates/          # HTML templates
├── static/             # Static files (CSS, JS)
└── media/              # Uploaded files
```

## License

MIT
