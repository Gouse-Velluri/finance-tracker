# 💰 FinanceTracker

A full-featured personal finance management web application built with Django 5.

![Django](https://img.shields.io/badge/Django-5.0-green) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)

---

## ✨ Features

- 🔐 **Authentication** — Register, login, logout, password reset via email
- 📊 **Dashboard** — Real-time income/expense summary with Chart.js bar + pie charts
- 💸 **Expense Tracking** — Full CRUD, search, filter by date/category/amount, CSV export
- 💰 **Income Tracking** — Full CRUD with categories and CSV export
- 🏷️ **Category Management** — Custom categories with icons and colors; defaults auto-created
- 🌙 **Dark Mode** — Toggle persists per-user via database
- 📤 **CSV Export** — Download all expenses or income anytime
- 📱 **Responsive** — Bootstrap 5 mobile-first design
- 🔒 **Security** — CSRF, login-required, user-scoped queries
- ⚡ **AJAX Delete** — Delete without page reload
- 📄 **Pagination** — Configurable items per page
- 👤 **Profile** — Picture upload, currency symbol preference

---

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
git clone <repo-url>
cd finance_tracker
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate:
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your settings. At minimum, change `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Seed Sample Data (Optional)

```bash
python manage.py seed_data
# Login: demo / Demo@1234
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

Open: **http://127.0.0.1:8000**

---

## 📁 Project Structure

```
finance_tracker/
├── finance_tracker/          # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── expenses/                 # Main app
│   ├── models.py             # UserProfile, Category, Expense, Income
│   ├── views.py              # All CBVs
│   ├── forms.py              # ModelForms
│   ├── urls.py               # URL patterns
│   ├── admin.py
│   ├── context_processors.py # Dark mode + currency injection
│   └── management/
│       └── commands/
│           └── seed_data.py  # Demo data command
├── templates/
│   ├── base.html             # Master template
│   ├── landing.html
│   ├── partials/
│   │   ├── navbar.html
│   │   └── footer.html
│   ├── registration/         # Auth templates
│   ├── expenses/             # App templates
│   └── errors/               # 404, 500 pages
├── static/
│   ├── css/main.css
│   └── js/main.js
├── media/                    # User uploads
├── requirements.txt
├── .env.example
└── manage.py
```

---

## 📧 Email Password Reset Setup

For production email (Gmail), create an [App Password](https://support.google.com/accounts/answer/185833) and set in `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

For development, emails are printed to the console (default setting).

---

## 🌐 Production Deployment

### Heroku / Railway

```bash
# Install gunicorn (already in requirements.txt)
# Set environment variables in dashboard:
DEBUG=False
SECRET_KEY=<new-secure-key>
ALLOWED_HOSTS=yourdomain.com

# Collect static files
python manage.py collectstatic --no-input

# Run with gunicorn
gunicorn finance_tracker.wsgi:application
```

### Nginx + Gunicorn (VPS)

```bash
gunicorn finance_tracker.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120
```

Configure Nginx to proxy to port 8000 and serve `/media/` and `/static/` directly.

---

## 🔮 Future Integrations (Scalability)

This project is structured to easily add:

| Feature | How |
|--------|-----|
| REST API | Add `djangorestframework` + `expenses/api/` directory |
| React Frontend | Point React at the DRF API endpoints |
| Budget Alerts | Django management command + Celery periodic task |
| AI Insights | Call OpenAI/Claude API from a view with spending data |
| Payment Tracking | New `Payment` model + recurring expense logic |

---

## 🛡️ Security Checklist (Production)

- [ ] `DEBUG=False`
- [ ] Strong unique `SECRET_KEY`
- [ ] `ALLOWED_HOSTS` restricted to your domain
- [ ] `HTTPS` with `SECURE_SSL_REDIRECT=True`
- [ ] Database backups configured
- [ ] Static files served via CDN/Nginx

---

## 📝 License

MIT License. Free to use and modify.
