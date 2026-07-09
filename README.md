# HUUGIAU Atelier Fashion Website

HUUGIAU Atelier is a Django-based fashion storefront with an editorial UI, fast browsing, and simple local admin tools.

## Stack

- Python 3.10+
- Windows 11+
- PowerShell 7+
- Django 6.x
- SQLite
- HTML5 templates
- CSS3
- JavaScript
- Django REST Framework
- Pillow
- NumPy
- Requests
- YAML

## Docs

- [Installation guide](docs/installation.md)
- [Running guide](docs/running.md)

## Main features

- Editorial homepage with a large hero and featured products
- Catalog filters by category, size, color, price, and sorting
- Product detail page with gallery, variants, wishlist, and cart
- Checkout, bank QR payment, and order tracking
- Login, register, wishlist, and account pages
- Staff dashboard

## Quick start

```powershell
.\scripts\run_local.ps1
```

## Repo layout

- `backend/`: Django apps, models, views, commands
- `frontend/`: templates, CSS, JavaScript, static assets
- `database/`: seed data and related files
- `scripts/`: PowerShell helpers for local run and smoke test
- `docs/`: install and run docs

## Notes

- The project uses SQLite by default
- The UI is tuned for a small storefront: read fast, browse fast, buy fast
- If old CSS or JS is cached, do a hard refresh
