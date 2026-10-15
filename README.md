## Products application

The products application manages:

- Categories and nested categories.
- Brands and optional brand logos.
- Products, prices and stock.
- Product images.
- Product attributes and their values.

All six models are registered in Django Admin.
The admin includes search, filters, automatic slug filling,
and inline forms for product images and attribute values.

[Products ER diagram](docs/products-erd.md)

### Local verification

From the market_catalog_API directory, using the project's
virtual environment:

    python manage.py check
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Open http://127.0.0.1:8000/admin/ and sign in.