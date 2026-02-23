# 🎟️ Event Booking API

A RESTful seat booking API built with **Django 6**, **Django REST Framework**, and **MongoDB** (via `django-mongodb-backend`). It allows users to view, book, and cancel event seats — with built-in rate limiting to prevent abuse.

---

## 🚀 Features

- **View all seats** — see which seats are available, booked, and who booked them
- **Book seats** — reserve one or multiple seats by name (up to 10 per user)
- **Cancel seats** — release previously booked seats
- **Rate limiting** — IP-based middleware blocks IPs that exceed 10 requests/minute for 60 seconds
- **Atomic transactions** — concurrent booking conflicts are safely handled

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 6.0 |
| API | Django REST Framework |
| Database | MongoDB Atlas (via `django-mongodb-backend`) |
| Language | Python 3.14+ |

---

## 📁 Project Structure

```
eventbooking/
├── booking/                  # Core app
│   ├── models.py             # Seat model
│   ├── views.py              # API view logic
│   ├── serializer.py         # DRF serializer
│   ├── urls.py               # App-level URL routes
│   ├── middleware.py         # IP-based rate limiting
│   └── migrations/           # DB migrations
├── eventbooking/             # Project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── mongo_migrations/         # MongoDB-specific migrations
│   ├── admin/
│   ├── auth/
│   └── contenttypes/
└── manage.py
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd eventbooking
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install django djangorestframework django-mongodb-backend
```

### 4. Configure the database

Open `eventbooking/settings.py` and update the `DATABASES` section with your MongoDB Atlas connection string:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_mongodb_backend',
        'HOST': 'mongodb+srv://<username>:<password>@<cluster>.mongodb.net/',
        'NAME': 'eventdb',
    }
}
```

> ⚠️ **Never commit credentials to version control.** Use environment variables or a `.env` file in production.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

---

## 📡 API Reference

Base URL: `http://localhost:8000/api/`

---

### `GET /api/seats/`

Returns all seats grouped by status.

**Response:**
```json
{
  "allSeats": [
    { "seat_id": "A1", "booked": false, "name": null },
    { "seat_id": "A2", "booked": true, "name": "Alice" }
  ],
  "bookedSeats": [
    { "seat_id": "A2", "name": "Alice" }
  ],
  "availableSeats": [
    { "seat_id": "A1" }
  ]
}
```

---

### `POST /api/book/`

Books one or more seats for a user.

**Request Body:**
```json
{
  "name": "Alice",
  "seat_id": ["A1", "A3"]
}
```

> `seat_id` accepts either a single string or a list of strings.

**Success Response (200):**
```json
{ "message": "seats booked" }
```

**Error Responses:**

| Status | Reason |
|---|---|
| `400` | Missing `name` or `seat_id` |
| `400` | User already has 10 seats booked |
| `400` | One or more seats already taken |
| `404` | Seat ID does not exist |

---

### `POST /api/cancel/`

Cancels one or more previously booked seats.

**Request Body:**
```json
{
  "name": "Alice",
  "seat_id": ["A1"]
}
```

**Success Response (200):**
```json
{ "message": "seats cancelled" }
```

**Error Responses:**

| Status | Reason |
|---|---|
| `400` | Missing `name` or `seat_id` |
| `400` | Seat is booked under a different name |
| `404` | Seat ID does not exist |

---

## 🛡️ Rate Limiting

The `RateLimitMiddleware` enforces a limit of **10 requests per minute per IP address**. If the limit is exceeded, the IP is blocked for **60 seconds** and receives:

```json
{ "error": "Too many requests" }
```
```json
{ "error": "Blocked for 1 minute" }
```

Both return HTTP status `429`.

---

## 🗄️ Data Model

### `Seat`

| Field | Type | Description |
|---|---|---|
| `row` | `CharField(1)` | Row letter (e.g., `A`, `B`) |
| `number` | `IntegerField` | Seat number within the row |
| `seat_id` | `CharField(5)` | Auto-generated composite key (e.g., `A1`) |
| `booked` | `BooleanField` | Booking status (default: `False`) |
| `name` | `CharField(100)` | Name of the person who booked the seat |

`seat_id` is automatically set on save as `f"{row}{number}"` and is unique.

---

## 🔧 Configuration Notes

- `DEFAULT_AUTO_FIELD` is set to `ObjectIdAutoField` for MongoDB compatibility.
- Django admin, auth, and contenttypes apps use custom MongoDB migrations located in `mongo_migrations/`.
- The `DATABASE_ROUTERS` setting uses `MongoRouter` to correctly route queries.

---

## 🚧 Known Limitations & Future Improvements

- Rate limiting state is stored **in-memory** — it resets on server restart and does not work correctly with multiple workers. Consider using Redis for production rate limiting.
- No user authentication — bookings are name-based only.
- No seat initialization script — seats must be added manually (via admin or a management command).
- The secret key and DB credentials are currently hardcoded; move them to environment variables before deploying.

---

## 📄 License

MIT License — feel free to use and modify.
