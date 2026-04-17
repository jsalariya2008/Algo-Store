# ALGO — Streetwear E-Commerce Platform

> **Wear Your Story** — A premium streetwear brand experience built with Flask + MySQL.

---

## 🏗️ Project Structure

```
algo/
├── app.py                  # Flask application & routes
├── schema.sql              # MySQL database schema + seed data
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
│
├── templates/
│   ├── base.html           # Base layout (nav, footer, grain overlay)
│   ├── index.html          # Homepage (hero, featured, drops, lookbook teaser)
│   ├── collection.html     # Product listing with filters
│   ├── product_detail.html # Single product view
│   ├── cart.html           # Shopping cart
│   ├── auth.html           # Login + Signup
│   ├── lookbook.html       # Visual gallery / lookbook
│   ├── admin.html          # Admin product dashboard
│   └── admin_product_form.html  # Add/edit product form
│
├── static/
│   ├── css/main.css        # Complete design system
│   ├── js/main.js          # Animations, interactions, cart
│   └── images/             # Static assets
│
└── uploads/
    └── products/           # User-uploaded product images
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.9+
- MySQL 8.0+
- pip

### 2. Clone & Install

```bash
git clone <repo>
cd algo
pip install -r requirements.txt
```

### 3. Database Setup

```bash
mysql -u root -p < schema.sql
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your MySQL credentials
```

### 5. Run

```bash
python app.py
# → http://localhost:5000
```

---

## 🔐 Admin Access

After running `schema.sql`, create an admin account via signup, then manually set `is_admin=1` in MySQL:

```sql
UPDATE users SET is_admin=1 WHERE email='your@email.com';
```

Admin panel: `http://localhost:5000/admin`

---

## 🗄️ Database Schema

| Table         | Purpose                          |
|---------------|----------------------------------|
| `users`       | Customer accounts + admins       |
| `products`    | Product catalog                  |
| `cart`        | (Session-based, expandable to DB)|
| `orders`      | Order history                    |
| `order_items` | Line items per order             |

---

## 🎨 Design System

**Typography**
- Display: Bebas Neue (headings, brand name)
- Serif: Playfair Display (editorial, quotes)
- Body: Crimson Pro (descriptions)
- Mono: DM Mono (labels, prices, UI text)

**Color Palette**
- `#c0392b` — Brand Red (CTAs, accents)
- `#0d0d0d` — Black (backgrounds, text)
- `#f0e6d3` — Beige (backgrounds, cards)
- `#faf6ef` — Cream (page background)
- `#8b6f47` — Earth (secondary text)
- `#c8b49a` — Sand (muted text)

---

## 🛣️ Routes

| Route                         | Method    | Description             |
|-------------------------------|-----------|-------------------------|
| `/`                           | GET       | Homepage                |
| `/collection`                 | GET       | Product listing         |
| `/product/<id>`               | GET       | Product detail          |
| `/cart`                       | GET       | Cart view               |
| `/cart/add`                   | POST      | Add item (JSON)         |
| `/cart/remove`                | POST      | Remove item (JSON)      |
| `/cart/update`                | POST      | Update quantity (JSON)  |
| `/login`                      | GET/POST  | User login              |
| `/signup`                     | GET/POST  | User signup             |
| `/logout`                     | GET       | Logout                  |
| `/lookbook`                   | GET       | Visual lookbook         |
| `/admin`                      | GET       | Admin dashboard         |
| `/admin/product/add`          | GET/POST  | Add product             |
| `/admin/product/edit/<id>`    | GET/POST  | Edit product            |
| `/admin/product/delete/<id>`  | POST      | Delete product          |

---

## 📱 Features

- ✅ **Homepage** — Hero with parallax, featured products, upcoming drops, lookbook teaser
- ✅ **Collection** — Grid layout with category filters, lazy-loaded images
- ✅ **Product Detail** — Size selector, add to cart, accordion details, related products
- ✅ **Cart** — Session-based, qty update, remove, running total
- ✅ **Auth** — Hashed passwords, session management, admin roles
- ✅ **Lookbook** — Multi-chapter gallery, drag-to-scroll, staggered animations
- ✅ **Admin** — CRUD products, image upload, inventory management
- ✅ **Upcoming Drops** — Blurred/locked poster display
- ✅ **Grain texture** — CSS SVG-based film grain overlay
- ✅ **Page transitions** — Fade in/out between pages
- ✅ **Responsive** — Mobile-first, Instagram-style scroll on small screens
- ✅ **Toast notifications** — Cart feedback

---

## 🚀 Production Deployment

```bash
# Use Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With Nginx reverse proxy (recommended)
# Set FLASK_ENV=production
# Use a strong SECRET_KEY
# Configure MySQL with proper credentials
```

---

*ALGO — Made in India. Made for the streets.*
