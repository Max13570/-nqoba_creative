markdown# NQOBA CREATIVE — Ideas Into Impact

Creative business website for Nqoba Creative in Mbabane, Eswatini.
Showcase services, portfolio, and allow customers to contact / order.

**Live Site:** https://nqoba-creative.onrender.com/
**Local:** http://127.0.0.1:8000/

---

## Features

- Home page with hero + featured services
- Services page with images + prices
- About page
- Portfolio page
- Contact page
- Mobile responsive
- Admin panel to add / edit services without code
- WhatsApp order button

## Tech Stack

- Python 3.13
- Django 5.1.15
- SQLite (local) / PostgreSQL (live on Render)
- HTML, CSS, Django Templates
- WhiteNoise for static files
- Render for hosting
- Git + GitHub

## Project Structure
nqoba_creative/
  config/
    settings.py
    urls.py
  shop/
    models.py
    views.py
    urls.py
    admin.py
    templates/shop/
      base.html
      home.html
      services.html
      about.html
      portfolio.html
      contact.html
    static/shop/
      logo.png
  media/services/
  manage.py
  requirements.txtjavascript
## Pages

| Page | URL |
| --- | --- |
| Home | `/` |
| Services | `/services/` |
| About | `/about/` |
| Portfolio | `/portfolio/` |
| Contact | `/contact/` |
| Admin | `/admin/` |

## How To Run Locally

```bash
cd Desktop/nqoba_creative
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserverOpen: http://127.0.0.1:8000/
How To Add A Service
Login to /admin/Click Services > Add ServiceFill Name, Description, Price, Upload ImageSave — it appears automatically on Home, Services, PortfolioHow To Deploy (Update Live Site)bashgit add .
git commit -m "Describe what you changed"
git pushRender rebuilds automatically in 1-2 minutes.
Models
Service: Name, Description, Price, Image, Created At
Order: Customer Name, Phone/Email, Service, Quantity, Message, Status
Author
Mancoba Maxwell Shabalala
Nqoba Creative — Mbabane, Eswatini
License
All rights reserved — Nqoba Creative © 2026
