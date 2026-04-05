# 🛍️ FrontStore API

> A full-featured e-commerce REST API built with Django REST Framework — powering products, collections, carts, orders, and customer management, secured with JWT authentication.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-4.x-green?style=flat-square&logo=django)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.x-red?style=flat-square)
![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.3-orange?style=flat-square)
![JWT](https://img.shields.io/badge/Auth-JWT-yellow?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

---

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [API Reference](#api-reference)
  - [Auth Endpoints](#auth-endpoints)
  - [Products](#products)
  - [Collections](#collections)
  - [Carts](#carts)
  - [Orders](#orders)
  - [Customers](#customers)
- [Query Parameters](#query-parameters)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

FontStore API is a production-ready Django REST Framework backend that implements a complete e-commerce data layer. It exposes a clean OpenAPI 3.0 schema and ships with interactive documentation out of the box — no additional tooling required to explore or test endpoints.

---

## Features

- 🔐 **JWT Authentication** via `djangorestframework-simplejwt` and `djoser`
- 📦 **Product Management** with images, reviews, filtering, search, and pagination
- 🗂️ **Collections** to group and feature products
- 🛒 **Anonymous Carts** using UUID-based sessions — no login required to add items
- 📋 **Order Placement** by converting a cart into an order
- 👤 **Customer Profiles** with Bronze / Silver / Gold membership tiers
- 📄 **Interactive API Docs** via Swagger UI and ReDoc (auto-generated from code)
- 🔍 **Advanced Filtering** — filter by price range, collection, search term, and ordering

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Framework | Django 4.x |
| API Layer | Django REST Framework |
| Auth | Djoser + SimpleJWT |
| Schema | drf-spectacular (OpenAPI 3.0) |
| Database | MySQL (recommended) / SQLite (dev) |

---

## Getting Started

### Prerequisites

- Python 3.10+
- pipenv 2026.1.0
- (Optional) MySQL for production

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/fokoda799/frontstore-api.git
cd frontstore-api
```

**2. Create and activate a virtual environment**

```bash
pip install pipenv
pipenv shell
```

**3. Install dependencies**

```bash
pipenv install
```

**4. Apply migrations**

```bash
python manage.py migrate
```

**5. (Optional) Load sample data**

```bash
python manage.py loaddata seed.json
```

**6. Create a superuser**

```bash
python manage.py createsuperuser
```

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (leave blank to use SQLite)
DATABASE_URL=mysql://user:password@localhost:5432/fontstore
```

> ⚠️ Never commit `.env` to version control. Add it to `.gitignore`.

### Running the Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000`.

---

## API Documentation

Once the server is running, three documentation views are available:

| Interface | URL | Description |
|---|---|---|
| **Swagger UI** | `/api/docs/` | Interactive explorer — try endpoints live |
| **ReDoc** | `/api/redoc/` | Clean three-panel reference docs |
| **OpenAPI Schema** | `/api/schema/?format=json` | Raw schema for tooling / client generation |

---

## Authentication

FontStore API uses **JWT (JSON Web Token)** authentication with the `JWT` prefix.

### 1. Obtain tokens

```http
POST /auth/jwt/create/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Response:

```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

### 2. Use the access token

Include the token in the `Authorization` header for all protected requests:

```http
Authorization: JWT <access_token>
```

### 3. Refresh an expired token

```http
POST /auth/jwt/refresh/
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

> **Public endpoints** (no auth required): creating a cart, browsing product images, and registering a new user.

---

## API Reference

### Auth Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/auth/users/` | Register a new user | Public |
| `POST` | `/auth/jwt/create/` | Obtain JWT access + refresh tokens | Public |
| `POST` | `/auth/jwt/refresh/` | Refresh an expired access token | Public |
| `POST` | `/auth/jwt/verify/` | Verify a token is valid | Public |
| `GET` | `/auth/users/me/` | Get the authenticated user | 🔐 |
| `PUT` / `PATCH` | `/auth/users/me/` | Update the authenticated user | 🔐 |
| `DELETE` | `/auth/users/me/` | Delete the authenticated user | 🔐 |
| `POST` | `/auth/users/set_password/` | Change password | 🔐 |
| `POST` | `/auth/users/reset_password/` | Request password reset email | Public |
| `POST` | `/auth/users/reset_password_confirm/` | Confirm password reset | Public |

---

### Products

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/store/products/` | List products (paginated, filterable) | 🔐 |
| `POST` | `/store/products/` | Create a product | 🔐 |
| `GET` | `/store/products/{id}/` | Retrieve a product | 🔐 |
| `PUT` / `PATCH` | `/store/products/{id}/` | Update a product | 🔐 |
| `DELETE` | `/store/products/{id}/` | Delete a product | 🔐 |
| `GET` | `/store/products/{id}/images/` | List product images | Public |
| `POST` | `/store/products/{id}/images/` | Upload a product image | Public |
| `DELETE` | `/store/products/{id}/images/{img_id}/` | Delete a product image | Public |
| `GET` | `/store/products/{id}/reviews/` | List reviews for a product | Public |
| `POST` | `/store/products/{id}/reviews/` | Submit a review | Public |

---

### Collections

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/store/collections/` | List all collections | 🔐 |
| `POST` | `/store/collections/` | Create a collection | 🔐 |
| `GET` | `/store/collections/{id}/` | Retrieve a collection | 🔐 |
| `PUT` / `PATCH` | `/store/collections/{id}/` | Update a collection | 🔐 |
| `DELETE` | `/store/collections/{id}/` | Delete a collection | 🔐 |

---

### Carts

Carts are identified by a UUID and do not require authentication.

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/store/carts/` | Create a new cart | Public |
| `GET` | `/store/carts/{id}/` | Retrieve a cart with its items | Public |
| `DELETE` | `/store/carts/{id}/` | Delete a cart | Public |
| `GET` | `/store/carts/{cart_pk}/items/` | List items in a cart | Public |
| `POST` | `/store/carts/{cart_pk}/items/` | Add an item to a cart | Public |
| `PATCH` | `/store/carts/{cart_pk}/items/{id}/` | Update item quantity | Public |
| `DELETE` | `/store/carts/{cart_pk}/items/{id}/` | Remove an item from a cart | Public |

**Add item example:**

```http
POST /store/carts/{cart_pk}/items/
Content-Type: application/json

{
  "product_id": 42,
  "quantity": 2
}
```

---

### Orders

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/store/orders/` | List the authenticated user's orders | 🔐 |
| `POST` | `/store/orders/` | Place an order from a cart | 🔐 |
| `GET` | `/store/orders/{id}/` | Retrieve an order | 🔐 |
| `PATCH` | `/store/orders/{id}/` | Update order payment status | 🔐 |
| `DELETE` | `/store/orders/{id}/` | Delete an order | 🔐 |

**Place an order:**

```http
POST /store/orders/
Authorization: JWT <access_token>
Content-Type: application/json

{
  "cart_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Payment status values:** `P` (Pending) · `C` (Completed) · `F` (Failed)

---

### Customers (Created automatically when you register)

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/store/costumers/` | List all customers (admin) | 🔐 |
| `POST` | `/store/costumers/` | Create a customer profile | 🔐 |
| `GET` | `/store/costumers/me/` | Get the authenticated customer's profile | 🔐 |
| `PUT` | `/store/costumers/me/` | Update the authenticated customer's profile | 🔐 |
| `GET` | `/store/costumers/{id}/` | Get a specific customer | 🔐 |
| `PUT` / `PATCH` | `/store/costumers/{id}/` | Update a specific customer | 🔐 |
| `DELETE` | `/store/costumers/{id}/` | Delete a customer | 🔐 |

**Membership tiers:** `B` (Bronze) · `S` (Silver) · `G` (Gold)

---

## Query Parameters

The `/store/products/` endpoint supports the following query parameters:

| Parameter | Type | Description | Example |
|---|---|---|---|
| `search` | string | Search by product title | `?search=sans` |
| `collection_id` | integer | Filter by collection | `?collection_id=3` |
| `price__gt` | number | Price greater than | `?price__gt=10` |
| `price__lt` | number | Price less than | `?price__lt=100` |
| `ordering` | string | Sort field (prefix `-` for descending) | `?ordering=-price` |
| `page` | integer | Pagination page number | `?page=2` |

**Combined example:**

```
GET /store/products/?collection_id=1&price__gt=5&price__lt=50&ordering=price&search=mono
```

---

## Project Structure

```
fontstore-api/
├── core/                   # Shared utilities and base models
├── store/                  # Main e-commerce app
│   ├── models.py           # Product, Collection, Cart, Order, Customer
│   ├── serializers.py      # DRF serializers
│   ├── views.py            # ViewSets
│   ├── urls.py             # Store URL routing
│   └── filters.py          # Product filtering logic
├── fontstore/              # Project settings and root URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt
├── manage.py
└── README.md
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

Please make sure your code follows the existing style and that all tests pass before submitting.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ using Django REST Framework · OpenAPI 3.0.3 · v1.0.0</sub>
</div>